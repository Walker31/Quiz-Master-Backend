from rest_framework import serializers
from .models import ExamType, Subject, Chapter, Tag, Question, QuestionOption


class ExamTypeSerializer(serializers.ModelSerializer):
    subject_count = serializers.IntegerField(source='subjects.count', read_only=True)

    class Meta:
        model = ExamType
        fields = ['id', 'name', 'slug', 'description', 'is_active',
                  'subject_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class SubjectSerializer(serializers.ModelSerializer):
    exam_type_name = serializers.CharField(source='exam_type.name', read_only=True)
    chapter_count = serializers.IntegerField(source='chapters.count', read_only=True)

    class Meta:
        model = Subject
        fields = ['id', 'exam_type', 'exam_type_name', 'name', 'code',
                  'order', 'chapter_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChapterSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source='subject.name', read_only=True)
    question_count = serializers.IntegerField(source='questions.count', read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'subject', 'subject_name', 'name', 'order',
                  'is_active', 'question_count', 'created_at']
        read_only_fields = ['id', 'created_at']


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug']


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'label', 'text', 'image', 'is_correct', 'order']
        read_only_fields = ['id']


class QuestionOptionAdminSerializer(QuestionOptionSerializer):
    """Includes is_correct — only for admin/teacher views."""
    pass


class QuestionOptionStudentSerializer(QuestionOptionSerializer):
    """Hides is_correct from students during an active quiz."""
    class Meta(QuestionOptionSerializer.Meta):
        fields = ['id', 'label', 'text', 'image', 'order']


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionAdminSerializer(many=True, read_only=True)
    chapter_name = serializers.CharField(source='chapter.name', read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True, write_only=True,
        source='tags', required=False
    )

    class Meta:
        model = Question
        fields = [
            'id', 'chapter', 'chapter_name', 'q_type', 'difficulty',
            'text', 'image', 'solution', 'solution_video',
            'marks_correct', 'marks_wrong', 'marks_partial',
            'tags', 'tag_ids', 'created_by', 'is_verified', 'year',
            'options', 'created_at',
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        question = Question.objects.create(**validated_data)
        question.tags.set(tags)
        return question

    def update(self, instance, validated_data):
        tags = validated_data.pop('tags', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class QuestionStudentSerializer(QuestionSerializer):
    """Question serializer for students — hides solution and correct answers."""
    options = QuestionOptionStudentSerializer(many=True, read_only=True)

    class Meta(QuestionSerializer.Meta):
        fields = [
            'id', 'chapter', 'q_type', 'difficulty',
            'text', 'image', 'marks_correct', 'marks_wrong', 'marks_partial',
            'options',
        ]
