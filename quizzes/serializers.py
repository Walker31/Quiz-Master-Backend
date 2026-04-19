from rest_framework import serializers
from .models import Subject, Chapter, Quiz, Question, Score
from users.serializers import UserSerializer

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = '__all__'

class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chapter
        fields = '__all__'

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = '__all__'

class QuestionSerializer(serializers.ModelSerializer):
    subject = serializers.StringRelatedField(read_only=True)
    chapter = serializers.StringRelatedField(read_only=True)
    difficulty_label = serializers.CharField(source='get_difficulty_level_display', read_only=True)
    
    # Provide options as an array for frontend compatibility
    options = serializers.SerializerMethodField()
    text = serializers.CharField(source='question_statement', read_only=True)

    class Meta:
        model = Question
        fields = ['id', 'quiz', 'chapter', 'subject', 'text', 'question_statement', 
                  'option_1', 'option_2', 'option_3', 'option_4', 'options',
                  'correct_option', 'difficulty_level', 'difficulty_label', 
                  'remarks', 'created_at', 'updated_at']
    
    def get_options(self, obj):
        """Return options as an array"""
        return [
            {'id': 1, 'text': obj.option_1},
            {'id': 2, 'text': obj.option_2},
            {'id': 3, 'text': obj.option_3},
            {'id': 4, 'text': obj.option_4},
        ]

class ScoreSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    quiz = QuizSerializer(read_only=True)
    
    class Meta:
        model = Score
        fields = '__all__'
        
class ScoreCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ['quiz', 'time_taken', 'max_marks', 'total_scored']
