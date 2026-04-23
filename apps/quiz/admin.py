from django.contrib import admin
from .models import Quiz, QuizSection, QuizQuestion, QuizAssignment


class QuizQuestionInline(admin.TabularInline):
    """Inline admin for QuizQuestion — edit quiz questions directly within QuizSection."""
    model = QuizQuestion
    extra = 1
    fields = ('question', 'order', 'marks_correct', 'marks_wrong')
    ordering = ('order',)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related('question', 'section')


class QuizSectionInline(admin.TabularInline):
    """Inline admin for QuizSection — edit sections directly within Quiz."""
    model = QuizSection
    extra = 1
    fields = ('subject', 'name', 'order', 'duration_mins', 'max_questions')
    ordering = ('order',)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    """
    Admin interface for Quiz model.
    Includes inline editing of sections and comprehensive configuration.
    """
    list_display = ('title', 'status', 'access_type', 'exam_type', 'created_by', 
                    'section_count', 'question_count', 'start_time', 'created_at')
    list_filter = ('status', 'access_type', 'exam_type', 'created_by', 'created_at', 
                   'shuffle_questions', 'shuffle_options', 'is_proctored')
    search_fields = ('title', 'created_by__username', 'exam_type__name')
    filter_horizontal = ()
    inlines = [QuizSectionInline]
    readonly_fields = ('created_at', 'updated_at', 'section_count', 'question_count')
    
    fieldsets = (
        ('Basic Information', {'fields': ('title', 'exam_type', 'created_by')}),
        ('Status & Access', {'fields': ('status', 'access_type')}),
        ('Scheduling', {'fields': ('start_time', 'end_time', 'duration_mins')}),
        ('Behavior', {
            'fields': ('shuffle_questions', 'shuffle_options', 'show_solution_after', 
                      'max_attempts', 'pass_percentage'),
            'description': 'Configure quiz behavior and solution release.',
        }),
        ('Proctoring', {'fields': ('is_proctored',), 'classes': ('collapse',)}),
        ('Instructions', {'fields': ('instructions',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-created_at',)
    
    def section_count(self, obj):
        return obj.sections.count()
    section_count.short_description = 'Sections'
    
    def question_count(self, obj):
        return QuizQuestion.objects.filter(section__quiz=obj).count()
    question_count.short_description = 'Total Questions'


@admin.register(QuizSection)
class QuizSectionAdmin(admin.ModelAdmin):
    """Admin interface for QuizSection model."""
    list_display = ('name', 'quiz', 'subject', 'order', 'duration_mins', 
                    'question_count', 'created_at')
    list_filter = ('quiz__status', 'quiz__exam_type', 'subject', 'created_at')
    search_fields = ('name', 'quiz__title', 'subject__name')
    inlines = [QuizQuestionInline]
    readonly_fields = ('created_at', 'updated_at', 'question_count')
    
    fieldsets = (
        ('Basic Information', {'fields': ('quiz', 'subject', 'name')}),
        ('Ordering', {'fields': ('order',)}),
        ('Timing & Limits', {'fields': ('duration_mins', 'max_questions')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('quiz', 'order')
    
    def question_count(self, obj):
        return obj.quiz_questions.count()
    question_count.short_description = 'Questions'


@admin.register(QuizQuestion)
class QuizQuestionAdmin(admin.ModelAdmin):
    """Admin interface for QuizQuestion model."""
    list_display = ('id', 'section', 'question_preview', 'order', 'question_type', 
                    'marks_correct_display', 'marks_wrong_display', 'created_at')
    list_filter = ('section__quiz__status', 'section__quiz__exam_type', 'section', 
                   'question__q_type', 'created_at')
    search_fields = ('question__text', 'section__name', 'section__quiz__title')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Mapping', {'fields': ('section', 'question', 'order')}),
        ('Mark Overrides', {
            'fields': ('marks_correct', 'marks_wrong'),
            'description': 'Leave blank to use the question\'s default marks.',
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('section', 'order')
    
    def question_preview(self, obj):
        text = obj.question.text[:60].replace('\n', ' ').strip()
        return f"Q{obj.question.id}: {text}..."
    question_preview.short_description = 'Question'
    
    def question_type(self, obj):
        return obj.question.get_q_type_display()
    question_type.short_description = 'Type'
    
    def marks_correct_display(self, obj):
        if obj.marks_correct is not None:
            return f"{obj.marks_correct} (override)"
        return f"{obj.question.marks_correct} (default)"
    marks_correct_display.short_description = 'Marks Correct'
    
    def marks_wrong_display(self, obj):
        if obj.marks_wrong is not None:
            return f"{obj.marks_wrong} (override)"
        return f"{obj.question.marks_wrong} (default)"
    marks_wrong_display.short_description = 'Marks Wrong'


@admin.register(QuizAssignment)
class QuizAssignmentAdmin(admin.ModelAdmin):
    """Admin interface for QuizAssignment model."""
    list_display = ('id', 'quiz', 'assigned_to_display', 'batch', 'created_at', 'updated_at')
    list_filter = ('quiz__status', 'quiz__exam_type', 'quiz', 'created_at')
    search_fields = ('quiz__title', 'assigned_to__username', 'batch__name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Quiz Assignment', {'fields': ('quiz',)}),
        ('Student Assignment', {
            'fields': ('assigned_to',),
            'description': 'Assign to a specific student. Leave blank if assigning to batch.',
        }),
        ('Batch Assignment', {
            'fields': ('batch',),
            'description': 'Assign to an entire batch. Leave blank if assigning to student.',
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-created_at',)
    
    def assigned_to_display(self, obj):
        if obj.assigned_to:
            return f"{obj.assigned_to.username}"
        return "—"
    assigned_to_display.short_description = 'Assigned To'
