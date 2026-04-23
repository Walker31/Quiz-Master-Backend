from django.contrib import admin
from .models import ExamType, Subject, Chapter, Question, QuestionOption, Tag


@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    """Admin interface for ExamType model."""
    list_display = ('name', 'slug', 'is_active', 'subject_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'slug')}),
        ('Details', {'fields': ('description',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('name',)
    
    def subject_count(self, obj):
        return obj.subjects.count()
    subject_count.short_description = 'Subjects'


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for Subject model."""
    list_display = ('name', 'exam_type', 'code', 'order', 'chapter_count', 'question_count')
    list_filter = ('exam_type', 'created_at')
    search_fields = ('name', 'code', 'exam_type__name')
    ordering = ('exam_type', 'order', 'name')
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'code', 'exam_type')}),
        ('Ordering', {'fields': ('order',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def chapter_count(self, obj):
        return obj.chapters.count()
    chapter_count.short_description = 'Chapters'
    
    def question_count(self, obj):
        return obj.chapters.values_list('questions', flat=True).count()
    question_count.short_description = 'Questions'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """Admin interface for Chapter model."""
    list_display = ('name', 'subject', 'order', 'is_active', 'question_count', 'created_at')
    list_filter = ('is_active', 'subject__exam_type', 'subject', 'created_at')
    search_fields = ('name', 'subject__name')
    ordering = ('subject', 'order', 'name')
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'subject')}),
        ('Ordering', {'fields': ('order',)}),
        ('Status', {'fields': ('is_active',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


class QuestionOptionInline(admin.TabularInline):
    """Inline admin for QuestionOption — edit options directly within Question."""
    model = QuestionOption
    extra = 4
    fields = ('label', 'text', 'image', 'is_correct', 'explanation')
    ordering = ('label',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """
    Admin interface for Question model.
    Includes inline editing of options and comprehensive filtering.
    """
    list_display = ('id', 'question_preview', 'chapter', 'q_type', 'difficulty', 
                    'is_verified', 'marks_correct', 'option_count', 'created_at')
    list_filter = ('q_type', 'difficulty', 'is_verified', 'chapter__subject__exam_type', 
                   'chapter', 'created_at', 'year')
    search_fields = ('text', 'id', 'chapter__name', 'chapter__subject__name')
    filter_horizontal = ('tags',)
    inlines = [QuestionOptionInline]
    readonly_fields = ('created_at', 'updated_at', 'option_count')
    
    fieldsets = (
        ('Basic Information', {'fields': ('chapter', 'q_type', 'difficulty', 'id')}),
        ('Question Content', {
            'fields': ('text', 'image'),
            'description': 'Use $...$ for inline LaTeX and $$....$$ for display math.',
        }),
        ('Solution', {'fields': ('solution', 'solution_video'), 'classes': ('collapse',)}),
        ('Marking Scheme', {'fields': ('marks_correct', 'marks_wrong', 'marks_partial')}),
        ('Metadata', {'fields': ('tags', 'created_by', 'is_verified', 'year')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-created_at',)
    
    def question_preview(self, obj):
        text = obj.text[:80].replace('\n', ' ').strip()
        return f"Q{obj.id}: {text}..."
    question_preview.short_description = 'Question Preview'
    
    def option_count(self, obj):
        return obj.options.count()
    option_count.short_description = 'Options'


@admin.register(QuestionOption)
class QuestionOptionAdmin(admin.ModelAdmin):
    """Admin interface for QuestionOption model."""
    list_display = ('id', 'question', 'label', 'text_preview', 'is_correct', 'created_at')
    list_filter = ('is_correct', 'question__q_type', 'created_at')
    search_fields = ('text', 'question__text', 'question__id')
    ordering = ('question', 'label')
    
    fieldsets = (
        ('Question Mapping', {'fields': ('question', 'label')}),
        ('Content', {'fields': ('text', 'image')}),
        ('Correctness', {'fields': ('is_correct',)}),
        ('Explanation', {'fields': ('explanation',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def text_preview(self, obj):
        text = obj.text[:60].replace('\n', ' ').strip()
        return f"{text}..." if len(obj.text) > 60 else text
    text_preview.short_description = 'Text Preview'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Admin interface for Tag model."""
    list_display = ('name', 'slug', 'question_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'slug')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('name',)
    
    def question_count(self, obj):
        return obj.question_set.count()
    question_count.short_description = 'Questions'
