from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.quiz.models import Quiz, QuizQuestion
from .models import QuizAttempt, QuestionResponse, QuestionEvent
from .serializers import (
    QuizAttemptSerializer, QuizAttemptStudentSerializer,
    QuestionResponseSerializer, QuestionEventSerializer
)
from .services import AttemptEvaluator


class QuizAttemptViewSet(viewsets.ModelViewSet):
    """
    Students: start, update, submit attempts.
    Admins: review all attempts.
    """
    queryset = QuizAttempt.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.user.is_admin:
            return QuizAttemptSerializer
        return QuizAttemptStudentSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin:
            return QuizAttempt.objects.filter(quiz__created_by=user)
        return QuizAttempt.objects.filter(student=user)

    @action(detail=False, methods=['post'], url_path='start')
    def start_attempt(self, request):
        """
        Starts a new quiz attempt. Validates max_attempts and timing.
        """
        quiz_id = request.data.get('quiz_id')
        quiz = get_object_or_404(Quiz, pk=quiz_id)

        # 1. Validate if student can attempt
        existing_count = QuizAttempt.objects.filter(student=request.user, quiz=quiz).count()
        if existing_count >= quiz.max_attempts:
            return Response({'detail': 'Max attempts reached.'}, status=403)

        # 2. Create the attempt
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            attempt_number=existing_count + 1,
            ip_address=request.META.get('REMOTE_ADDR'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )

        # 3. Initialize responses for ALL questions in the quiz
        # This allows the frontend to have IDs for every question slot immediately.
        quiz_questions = QuizQuestion.objects.filter(section__quiz=quiz)
        responses = [
            QuestionResponse(attempt=attempt, quiz_question=qq)
            for qq in quiz_questions
        ]
        QuestionResponse.objects.bulk_create(responses)

        return Response(QuizAttemptStudentSerializer(attempt).data, status=201)

    @action(detail=True, methods=['post'], url_path='heartbeat')
    def heartbeat(self, request, pk=None):
        """Updates elapsed time and last activity."""
        attempt = self.get_object()
        if attempt.status != 'IN_PROGRESS':
            return Response({'detail': 'Attempt not in progress.'}, status=400)
        
        attempt.time_elapsed_secs = request.data.get('elapsed_secs', attempt.time_elapsed_secs)
        attempt.save(update_fields=['time_elapsed_secs', 'last_activity_at'])
        return Response({'status': 'ok'})

    @action(detail=True, methods=['post'], url_path='respond')
    def respond(self, request, pk=None):
        """Updates answer for a single question and logs an event."""
        attempt = self.get_object()
        if attempt.status != 'IN_PROGRESS':
            return Response({'detail': 'Attempt not in progress.'}, status=400)

        qq_id = request.data.get('quiz_question_id')
        response = get_object_or_404(QuestionResponse, attempt=attempt, quiz_question_id=qq_id)

        # Update visit status and answers
        response.visit_status = request.data.get('visit_status', 'ANSWERED')
        if 'selected_options' in request.data:
            response.selected_options.set(request.data['selected_options'])
        if 'integer_answer' in request.data:
            response.integer_answer = request.data['integer_answer']
        if 'text_answer' in request.data:
            response.text_answer = request.data['text_answer']
        
        response.time_spent_secs = request.data.get('time_spent_secs', response.time_spent_secs)
        response.save()

        # Log Event
        QuestionEvent.objects.create(
            attempt=attempt,
            quiz_question_id=qq_id,
            event_type='ANSWER',
            time_on_q_secs=response.time_spent_secs,
            payload=request.data
        )

        return Response({'status': 'saved'})

    @action(detail=True, methods=['post'], url_path='proctor-event')
    def log_proctor_event(self, request, pk=None):
        """Logs a proctoring event like tab switch or fullscreen exit."""
        attempt = self.get_object()
        if attempt.status != 'IN_PROGRESS':
            return Response({'detail': 'Attempt not in progress.'}, status=400)

        event_type = request.data.get('type') # 'TAB_SWITCH' or 'FULLSCREEN_EXIT'
        if event_type == 'TAB_SWITCH':
            attempt.tab_switch_count += 1
        elif event_type == 'FULLSCREEN_EXIT':
            attempt.fullscreen_exits += 1
        
        attempt.save(update_fields=['tab_switch_count', 'fullscreen_exits'])
        
        # Also log to QuestionEvent for audit trail
        QuestionEvent.objects.create(
            attempt=attempt,
            quiz_question=None, # System level event
            event_type='LEAVE',
            time_on_q_secs=attempt.time_elapsed_secs,
            payload={'proctor_type': event_type}
        )
        
        return Response({'status': 'logged'})

    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """Evaluates the attempt and returns results."""
        attempt = self.get_object()
        if attempt.status != 'IN_PROGRESS':
            return Response({'detail': 'Already submitted.'}, status=400)

        evaluator = AttemptEvaluator()
        results = evaluator.evaluate(attempt)
        
        return Response(results)
