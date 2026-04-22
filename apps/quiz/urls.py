from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet, QuizSectionViewSet,
    QuizQuestionViewSet, QuizAssignmentViewSet
)

router = DefaultRouter()
router.register(r'quizzes', QuizViewSet, basename='quiz')
router.register(r'sections', QuizSectionViewSet, basename='quiz-section')
router.register(r'questions', QuizQuestionViewSet, basename='quiz-question')
router.register(r'assignments', QuizAssignmentViewSet, basename='quiz-assignment')

urlpatterns = [
    path('', include(router.urls)),
]
