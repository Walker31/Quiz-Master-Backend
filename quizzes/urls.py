from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SubjectViewSet, ChapterViewSet, QuizViewSet, QuestionViewSet, ScoreViewSet

router = DefaultRouter()
router.register(r'subjects', SubjectViewSet)
router.register(r'chapters', ChapterViewSet)
router.register(r'quizzes', QuizViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'scores', ScoreViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
