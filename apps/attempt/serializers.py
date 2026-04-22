from rest_framework import serializers
from apps.quiz.serializers import QuizSerializer, QuizQuestionSerializer
from .models import QuizAttempt, QuestionResponse, QuestionEvent


class QuestionResponseSerializer(serializers.ModelSerializer):
    """Admin-facing: includes marks and correct flag."""
    class Meta:
        model = QuestionResponse
        fields = [
            'id', 'quiz_question', 'visit_status', 'selected_options',
            'integer_answer', 'text_answer', 'time_spent_secs',
            'is_correct', 'marks_awarded', 'is_manually_graded'
        ]


class QuestionResponseStudentSerializer(serializers.ModelSerializer):
    """Student-facing during quiz: hides results."""
    class Meta:
        model = QuestionResponse
        fields = [
            'id', 'quiz_question', 'visit_status', 'selected_options',
            'integer_answer', 'text_answer', 'time_spent_secs'
        ]


class QuizAttemptSerializer(serializers.ModelSerializer):
    responses = QuestionResponseSerializer(many=True, read_only=True)
    quiz_info = QuizSerializer(source='quiz', read_only=True)
    student_name = serializers.CharField(source='student.username', read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            'id', 'student', 'student_name', 'quiz', 'quiz_info',
            'attempt_number', 'status', 'started_at', 'submitted_at',
            'time_elapsed_secs', 'total_marks', 'marks_obtained',
            'correct_count', 'wrong_count', 'skipped_count',
            'percentile', 'rank', 'is_passed', 'responses'
        ]
        read_only_fields = ['id', 'started_at', 'submitted_at', 'rank', 'percentile']


class QuizAttemptStudentSerializer(QuizAttemptSerializer):
    """Hides results from student if quiz doesn't allow immediate solutions."""
    responses = QuestionResponseStudentSerializer(many=True, read_only=True)

    class Meta(QuizAttemptSerializer.Meta):
        fields = [
            'id', 'quiz', 'quiz_info', 'attempt_number', 'status', 'started_at',
            'time_elapsed_secs', 'responses'
        ]


class QuestionEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionEvent
        fields = ['id', 'quiz_question', 'event_type', 'time_on_q_secs', 'payload']
