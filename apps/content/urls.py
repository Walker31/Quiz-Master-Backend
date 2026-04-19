from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ExamTypeViewSet, SubjectViewSet, ChapterViewSet,
    TagViewSet, QuestionViewSet,
)

router = DefaultRouter()
router.register(r'exam-types', ExamTypeViewSet, basename='exam-type')
router.register(r'subjects', SubjectViewSet, basename='subject')
router.register(r'chapters', ChapterViewSet, basename='chapter')
router.register(r'tags', TagViewSet, basename='tag')
router.register(r'questions', QuestionViewSet, basename='question')

urlpatterns = [
    path('', include(router.urls)),
]
