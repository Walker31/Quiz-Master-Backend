from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Subject, Chapter, Quiz, Question, Score
from .serializers import SubjectSerializer, ChapterSerializer, QuizSerializer, QuestionSerializer, ScoreSerializer, ScoreCreateSerializer

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Allow anyone to read (GET, HEAD, OPTIONS)
    Allow only authenticated staff/admins to write (POST, PUT, DELETE)
    """
    def has_permission(self, request, view):
        # Allow all GET, HEAD, OPTIONS requests
        if request.method in permissions.SAFE_METHODS:
            return True
        # For write operations, must be authenticated and staff
        return request.user and request.user.is_authenticated and request.user.is_staff

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]

class ChapterViewSet(viewsets.ModelViewSet):
    queryset = Chapter.objects.all()
    serializer_class = ChapterSerializer
    permission_classes = [IsAdminOrReadOnly]

class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    @action(detail=False, methods=['get'])
    def live(self, request):
        live_quizzes = Quiz.objects.filter(is_live=True)
        serializer = self.get_serializer(live_quizzes, many=True)
        return Response(serializer.data)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [IsAdminOrReadOnly]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        quiz_id = self.request.query_params.get('quiz', None)
        chapter_id = self.request.query_params.get('chapter', None)
        subject_id = self.request.query_params.get('subject', None)
        difficulty = self.request.query_params.get('difficulty', None)
        
        # Filter by quiz if provided and valid
        if quiz_id:
            if quiz_id != 'undefined':
                try:
                    quiz_id = int(quiz_id)
                    queryset = queryset.filter(quiz_id=quiz_id)
                except (ValueError, TypeError):
                    pass
        
        # Filter by chapter if provided and valid
        if chapter_id and chapter_id != 'undefined':
            try:
                chapter_id = int(chapter_id)
                queryset = queryset.filter(chapter_id=chapter_id)
            except (ValueError, TypeError):
                pass
        
        # Filter by subject if provided and valid
        if subject_id and subject_id != 'undefined':
            try:
                subject_id = int(subject_id)
                queryset = queryset.filter(subject_id=subject_id)
            except (ValueError, TypeError):
                pass
        
        # Filter by difficulty if provided and valid
        if difficulty and difficulty != 'undefined':
            try:
                difficulty = int(difficulty)
                queryset = queryset.filter(difficulty_level=difficulty)
            except (ValueError, TypeError):
                pass
        
        return queryset

class ScoreViewSet(viewsets.ModelViewSet):
    queryset = Score.objects.all()
    serializer_class = ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return Score.objects.all()
        return Score.objects.filter(user=self.request.user)
        
    def get_serializer_class(self):
        if self.action == 'create':
            return ScoreCreateSerializer
        return ScoreSerializer
        
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
