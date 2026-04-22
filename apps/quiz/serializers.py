from rest_framework import serializers
from apps.content.serializers import ExamTypeSerializer, SubjectSerializer, QuestionStudentSerializer
from .models import Quiz, QuizSection, QuizQuestion, QuizAssignment


class QuizQuestionSerializer(serializers.ModelSerializer):
    question_data = QuestionStudentSerializer(source='question', read_only=True)

    class Meta:
        model = QuizQuestion
        fields = ['id', 'section', 'question', 'question_data', 'order', 
                  'marks_correct', 'marks_wrong']


class QuizSectionSerializer(serializers.ModelSerializer):
    quiz_questions = QuizQuestionSerializer(many=True, read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = QuizSection
        fields = ['id', 'quiz', 'subject', 'subject_name', 'name', 'order',
                  'duration_mins', 'max_questions', 'quiz_questions']


class QuizSerializer(serializers.ModelSerializer):
    sections = QuizSectionSerializer(many=True, read_only=True)
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Quiz
        fields = [
            'id', 'title', 'exam_type', 'exam_type_name', 'created_by',
            'status', 'access_type', 'start_time', 'end_time', 'duration_mins',
            'shuffle_questions', 'shuffle_options', 'show_solution_after',
            'max_attempts', 'pass_percentage', 'instructions', 'is_proctored',
            'sections', 'question_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def get_question_count(self, obj):
        return QuizQuestion.objects.filter(section__quiz=obj).count()


class QuizAssignmentSerializer(serializers.ModelSerializer):
    quiz_title = serializers.CharField(source='quiz.title', read_only=True)
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True)
    batch_name = serializers.CharField(source='batch.name', read_only=True)

    class Meta:
        model = QuizAssignment
        fields = ['id', 'quiz', 'quiz_title', 'assigned_to', 'assigned_to_name',
                  'batch', 'batch_name', 'deadline', 'is_mandatory', 'assigned_by']
        read_only_fields = ['id', 'assigned_by']
