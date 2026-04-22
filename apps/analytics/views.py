from django.db.models import Count, Avg, Max
from rest_framework import views, permissions, status
from rest_framework.response import Response

from apps.accounts.models import User, Batch
from apps.quiz.models import Quiz
from apps.content.models import Question
from apps.attempt.models import QuizAttempt


class AdminDashboardStatsView(views.APIView):
    """
    Returns aggregated stats for the Admin Overview page.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not request.user.is_admin:
            return Response({'detail': 'Admin access required.'}, status=403)

        user = request.user
        
        # Superadmin sees everything; Admin sees their own created content
        if user.is_superadmin:
            total_students = User.objects.filter(role='STUDENT').count()
            total_quizzes = Quiz.objects.count()
            total_questions = Question.objects.count()
            active_exams = Quiz.objects.filter(status='PUBLISHED').count()
            avg_score = QuizAttempt.objects.filter(status='SUBMITTED').aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0
        else:
            total_students = User.objects.filter(batches__admin=user).distinct().count()
            total_quizzes = Quiz.objects.filter(created_by=user).count()
            total_questions = Question.objects.filter(created_by=user).count()
            active_exams = Quiz.objects.filter(created_by=user, status='PUBLISHED').count()
            avg_score = QuizAttempt.objects.filter(quiz__created_by=user, status='SUBMITTED').aggregate(Avg('marks_obtained'))['marks_obtained__avg'] or 0

        return Response({
            'total_students': total_students,
            'total_quizzes': total_quizzes,
            'total_questions': total_questions,
            'active_exams': active_exams,
            'avg_score': float(avg_score),
            'recent_activity': [] # To be populated with recent attempts
        })


class LeaderboardView(views.APIView):
    """
    Returns the top performers for a specific quiz.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, quiz_id):
        attempts = QuizAttempt.objects.filter(
            quiz_id=quiz_id, status='SUBMITTED'
        ).select_related('student').order_by('-marks_obtained', 'time_elapsed_secs')[:10]

        data = [
            {
                'rank': i + 1,
                'username': a.student.username,
                'full_name': f"{a.student.first_name} {a.student.last_name}",
                'score': float(a.marks_obtained),
                'time': a.time_elapsed_secs,
                'submitted_at': a.submitted_at
            }
            for i, a in enumerate(attempts)
        ]
        return Response(data)


class StudentPerformanceView(views.APIView):
    """
    Returns a student's quiz performance history.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        attempts = QuizAttempt.objects.filter(
            student=user, status='SUBMITTED'
        ).select_related('quiz').order_by('submitted_at')

        history = [
            {
                'quiz_title': a.quiz.title,
                'score': float(a.marks_obtained),
                'total': float(a.total_marks),
                'percentage': float((a.marks_obtained / a.total_marks) * 100) if a.total_marks > 0 else 0,
                'date': a.submitted_at
            }
            for a in attempts
        ]

        return Response({
            'history': history,
            'total_exams': len(history),
            'avg_percentage': sum(h['percentage'] for h in history) / len(history) if history else 0
        })
