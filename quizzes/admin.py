from django.contrib import admin
from .models import Subject, Chapter, Quiz, Question, Score

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for legacy Subject model."""
    list_display = ('name', 'chapter_count', 'quiz_count', 'created_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {'fields': ('name',)}),
        ('Description', {'fields': ('description',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('name',)
    
    def chapter_count(self, obj):
        return obj.chapters.count()
    chapter_count.short_description = 'Chapters'
    
    def quiz_count(self, obj):
        return obj.quizzes.count()
    quiz_count.short_description = 'Quizzes'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    """Admin interface for legacy Chapter model."""
    list_display = ('name', 'subject', 'quiz_count', 'created_at')
    list_filter = ('subject', 'created_at', 'updated_at')
    search_fields = ('name', 'subject__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {'fields': ('name', 'subject')}),
        ('Description', {'fields': ('description',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('subject', 'name')
    
    def quiz_count(self, obj):
        return obj.quizzes.count()
    quiz_count.short_description = 'Quizzes'


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """Admin interface for legacy Quiz model."""
    list_display = ('quiz_title', 'subject', 'chapter', 'date_of_quiz', 'time_duration', 'is_live', 'question_count')
    list_filter = ('is_live', 'subject', 'chapter', 'date_of_quiz', 'created_at')
    search_fields = ('quiz_title', 'subject__name', 'chapter__name', 'remarks')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {'fields': ('quiz_title', 'subject', 'chapter')}),
        ('Scheduling', {'fields': ('date_of_quiz', 'time_duration')}),
        ('Details', {'fields': ('remarks',)}),
        ('Status', {'fields': ('is_live',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-date_of_quiz',)
    
    def question_count(self, obj):
        return obj.questions.count()
    question_count.short_description = 'Questions'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Admin interface for legacy Question model."""
    list_display = ('id', 'question_text_preview', 'quiz', 'chapter', 'difficulty_level', 
                    'created_at')
    list_filter = ('difficulty_level', 'quiz__subject', 'quiz__chapter', 'created_at')
    search_fields = ('question_statement', 'id', 'quiz__quiz_title', 'chapter__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {'fields': ('id', 'quiz', 'chapter', 'subject')}),
        ('Question Content', {'fields': ('question_statement',)}),
        ('Options', {'fields': ('option_1', 'option_2', 'option_3', 'option_4', 'correct_option')}),
        ('Difficulty & Remarks', {'fields': ('difficulty_level', 'remarks')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-created_at',)
    
    def question_text_preview(self, obj):
        text = obj.question_statement[:80].replace('\n', ' ').strip()
        return f"Q{obj.id}: {text}..."
    question_text_preview.short_description = 'Question'


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    """Admin interface for legacy Score model."""
    list_display = ('id', 'user', 'quiz', 'total_scored', 'max_marks', 'percentage', 'time_taken_display', 'created_at')
    list_filter = ('quiz', 'quiz__subject', 'created_at')
    search_fields = ('user__username', 'quiz__quiz_title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Attempt Information', {'fields': ('user', 'quiz')}),
        ('Marks', {'fields': ('total_scored', 'max_marks')}),
        ('Timing', {'fields': ('time_taken',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-created_at',)
    
    def percentage(self, obj):
        if obj.max_marks > 0:
            return f"{(obj.total_scored / obj.max_marks * 100):.1f}%"
        return "—"
    percentage.short_description = 'Percentage'
    
    def time_taken_display(self, obj):
        if obj.time_taken:
            mins = obj.time_taken // 60
            secs = obj.time_taken % 60
            return f"{mins}m {secs}s"
        return "—"
    time_taken_display.short_description = 'Time Taken'
