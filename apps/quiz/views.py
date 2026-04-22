from django.utils.timezone import now
from django.db.models import Q
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsAdmin, IsAdminOrReadOnly
from .models import Quiz, QuizSection, QuizQuestion, QuizAssignment
from .serializers import (
    QuizSerializer, QuizSectionSerializer,
    QuizQuestionSerializer, QuizAssignmentSerializer
)


class QuizViewSet(viewsets.ModelViewSet):
    """
    Admin: Full access to their quizzes.
    Student: Can only list/retrieve published quizzes they are assigned to.
    """
    serializer_class = QuizSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return Quiz.objects.filter(created_by=user).prefetch_related('sections__quiz_questions')
        
        # Students: Quizzes that are published AND (Open OR Assigned directly OR via Batch)
        return Quiz.objects.filter(
            status='PUBLISHED'
        ).filter(
            Q(access_type='OPEN') |
            Q(assignments__assigned_to=user) |
            Q(assignments__batch__students=user)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], url_path='publish')
    def publish(self, request, pk=None):
        quiz = self.get_object()
        if not quiz.sections.exists():
            return Response({'detail': 'Cannot publish quiz without sections.'}, status=400)
        quiz.status = 'PUBLISHED'
        quiz.save()
        return Response({'status': 'published'})


class QuizSectionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizSectionSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return QuizSection.objects.filter(quiz__created_by=self.request.user)


class QuizQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuizQuestionSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return QuizQuestion.objects.filter(section__quiz__created_by=self.request.user)


class QuizAssignmentViewSet(viewsets.ModelViewSet):
    serializer_class = QuizAssignmentSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return QuizAssignment.objects.filter(assigned_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(assigned_by=self.request.user)
