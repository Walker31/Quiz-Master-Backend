import csv
import io

from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsAdmin, IsAdminOrReadOnly
from .models import ExamType, Subject, Chapter, Tag, Question, QuestionOption
from .serializers import (
    ExamTypeSerializer, SubjectSerializer, ChapterSerializer,
    TagSerializer, QuestionSerializer,
)


class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'slug']


class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.select_related('exam_type').all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'code']
    ordering_fields = ['order', 'name']
    filterset_fields = ['exam_type']

    def get_queryset(self):
        qs = super().get_queryset()
        exam_type = self.request.query_params.get('exam_type')
        if exam_type:
            qs = qs.filter(exam_type_id=exam_type)
        return qs


class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.select_related('subject__exam_type').all()
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['order', 'name']

    def get_queryset(self):
        qs = super().get_queryset()
        subject = self.request.query_params.get('subject')
        if subject:
            qs = qs.filter(subject_id=subject)
        return qs


class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminOrReadOnly]


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related(
        'chapter__subject__exam_type', 'created_by'
    ).prefetch_related('options', 'tags').all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAdmin]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['text', 'tags__name']
    ordering_fields = ['difficulty', 'created_at']

    def get_queryset(self):
        qs = super().get_queryset()
        for param in ('chapter', 'q_type', 'difficulty', 'is_verified'):
            val = self.request.query_params.get(param)
            if val:
                qs = qs.filter(**{param: val})
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['post'], url_path='bulk-import')
    def bulk_import(self, request):
        """
        CSV bulk import. Expected columns:
        chapter_id, q_type, difficulty, text,
        option_a, option_b, option_c, option_d, correct (A/B/C/D),
        marks_correct, marks_wrong, year (optional)
        """
        file = request.FILES.get('file')
        if not file:
            return Response({'detail': 'No file provided.'}, status=400)

        decoded = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(decoded))

        created, errors = [], []
        for i, row in enumerate(reader, start=2):  # row 1 = header
            try:
                chapter = Chapter.objects.get(pk=row['chapter_id'])
                question = Question.objects.create(
                    chapter=chapter,
                    q_type=row.get('q_type', 'MCQ_SINGLE').upper(),
                    difficulty=row.get('difficulty', 'MEDIUM').upper(),
                    text=row['text'],
                    marks_correct=row.get('marks_correct', 4),
                    marks_wrong=row.get('marks_wrong', -1),
                    year=row.get('year') or None,
                    created_by=request.user,
                )
                correct_label = row.get('correct', '').upper()
                for idx, label in enumerate(['A', 'B', 'C', 'D']):
                    opt_text = row.get(f'option_{label.lower()}', '').strip()
                    if opt_text:
                        QuestionOption.objects.create(
                            question=question,
                            label=label,
                            text=opt_text,
                            is_correct=(label == correct_label),
                            order=idx,
                        )
                created.append(question.id)
            except Exception as e:
                errors.append({'row': i, 'error': str(e)})

        return Response({
            'created': len(created),
            'errors': errors,
            'question_ids': created,
        }, status=207 if errors else 201)
