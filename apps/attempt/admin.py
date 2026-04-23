from django.contrib import admin
from django.utils.html import format_html
from .models import QuizAttempt, QuestionResponse, QuestionEvent, SectionTimer


class QuestionResponseInline(admin.TabularInline):
    """Inline admin for QuestionResponse — view responses within QuizAttempt."""
    model = QuestionResponse
    extra = 0
    can_delete = False
    fields = ('quiz_question', 'visit_status', 'is_correct', 'marks_awarded', 'time_spent_secs')
    readonly_fields = ('quiz_question', 'visit_status', 'is_correct', 'marks_awarded', 'time_spent_secs')
    
    def has_add_permission(self, request, obj=None):
        return False


class QuestionEventInline(admin.TabularInline):
    """Inline admin for QuestionEvent — view events within QuizAttempt."""
    model = QuestionEvent
    extra = 0
    can_delete = False
    fields = ('quiz_question', 'event_type', 'timestamp', 'time_on_q_secs')
    readonly_fields = ('quiz_question', 'event_type', 'timestamp', 'time_on_q_secs')
    ordering = ['-timestamp']
    
    def has_add_permission(self, request, obj=None):
        return False


class SectionTimerInline(admin.TabularInline):
    """Inline admin for SectionTimer — view section timers within QuizAttempt."""
    model = SectionTimer
    extra = 0
    can_delete = False
    fields = ('section', 'started_at', 'time_used_secs', 'is_completed')
    readonly_fields = ('section', 'started_at', 'time_used_secs', 'is_completed')
    ordering = ['section']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    """
    Admin interface for QuizAttempt model.
    Displays comprehensive attempt details with inline responses and events.
    """
    list_display = ('id', 'student_display', 'quiz', 'attempt_number', 'status_badge', 
                    'score_display', 'time_display', 'started_at', 'submitted_at')
    list_filter = ('status', 'quiz__status', 'quiz__exam_type', 'student', 
                   'started_at', 'submitted_at', 'is_passed')
    search_fields = ('student__username', 'student__email', 'quiz__title')
    readonly_fields = ('student', 'quiz', 'attempt_number', 'started_at', 'submitted_at',
                      'last_activity_at', 'time_elapsed_secs', 'total_marks', 'marks_obtained',
                      'correct_count', 'wrong_count', 'skipped_count', 'percentile', 'rank',
                      'is_passed', 'ip_address', 'user_agent', 'score_display_readonly',
                      'time_display_readonly', 'proctoring_summary')
    
    inlines = [QuestionResponseInline, SectionTimerInline, QuestionEventInline]
    
    fieldsets = (
        ('Attempt Information', {'fields': ('student', 'quiz', 'attempt_number', 'status')}),
        ('Timing', {
            'fields': ('started_at', 'submitted_at', 'last_activity_at', 'time_elapsed_secs'),
            'description': 'time_elapsed_secs is updated via heartbeat every 30 seconds.',
        }),
        ('Results', {
            'fields': ('total_marks', 'marks_obtained', 'score_display_readonly', 'is_passed',
                      'correct_count', 'wrong_count', 'skipped_count', 'percentile', 'rank'),
            'description': 'Results are populated when the attempt is submitted.',
            'classes': ('collapse',)
        }),
        ('Proctoring', {
            'fields': ('is_proctored_flag', 'tab_switch_count', 'fullscreen_exits', 'proctoring_summary'),
            'classes': ('collapse',)
        }),
        ('Technical Details', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
    )
    
    ordering = ('-started_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def get_readonly_fields(self, request, obj=None):
        # Make all fields readonly for non-superusers except status
        readonly = list(self.readonly_fields)
        if not request.user.is_superuser and obj:
            readonly.extend(['student', 'quiz', 'attempt_number'])
        return readonly
    
    def student_display(self, obj):
        return f"{obj.student.username} ({obj.student.email})"
    student_display.short_description = 'Student'
    
    def status_badge(self, obj):
        colors = {
            'IN_PROGRESS': 'orange',
            'SUBMITTED': 'green',
            'TIMED_OUT': 'red',
            'ABANDONED': 'gray',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def score_display(self, obj):
        if obj.marks_obtained is not None:
            return f"{obj.marks_obtained}/{obj.total_marks} ({obj.percentile or '—'}%)"
        return "—"
    score_display.short_description = 'Score'
    
    def score_display_readonly(self, obj):
        return self.score_display(obj)
    score_display_readonly.short_description = 'Final Score'
    
    def time_display(self, obj):
        mins = obj.time_elapsed_secs // 60
        secs = obj.time_elapsed_secs % 60
        return f"{mins}m {secs}s"
    time_display.short_description = 'Time'
    
    def time_display_readonly(self, obj):
        return self.time_display(obj)
    time_display_readonly.short_description = 'Time Spent'
    
    def is_proctored_flag(self, obj):
        return obj.quiz.is_proctored
    is_proctored_flag.short_description = 'Proctored'
    is_proctored_flag.boolean = True
    
    def proctoring_summary(self, obj):
        if not obj.quiz.is_proctored:
            return "Not proctored"
        return format_html(
            '<strong>Tab Switches:</strong> {} | <strong>Fullscreen Exits:</strong> {}',
            obj.tab_switch_count, obj.fullscreen_exits
        )
    proctoring_summary.short_description = 'Proctoring Summary'


@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    """Admin interface for QuestionResponse model."""
    list_display = ('id', 'attempt_display', 'quiz_question', 'visit_status', 'is_correct', 
                    'marks_awarded', 'time_spent_secs', 'created_at')
    list_filter = ('visit_status', 'is_correct', 'is_manually_graded', 
                   'attempt__quiz__status', 'attempt__quiz__exam_type', 'created_at')
    search_fields = ('attempt__student__username', 'quiz_question__question__text')
    readonly_fields = ('attempt', 'quiz_question', 'created_at', 'updated_at', 
                      'first_visited_at', 'last_answered_at')
    
    fieldsets = (
        ('Attempt Information', {'fields': ('attempt', 'quiz_question')}),
        ('Visit Status', {'fields': ('visit_status',)}),
        ('Student Answer', {
            'fields': ('selected_options', 'integer_answer', 'text_answer'),
            'description': 'Only one answer type will be populated depending on question type.',
        }),
        ('Timing', {
            'fields': ('first_visited_at', 'last_answered_at', 'time_spent_secs'),
            'classes': ('collapse',)
        }),
        ('Evaluation', {
            'fields': ('is_correct', 'marks_awarded', 'is_manually_graded'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-created_at',)
    
    def attempt_display(self, obj):
        return f"{obj.attempt.student.username} — {obj.attempt.quiz.title}"
    attempt_display.short_description = 'Attempt'


@admin.register(QuestionEvent)
class QuestionEventAdmin(admin.ModelAdmin):
    """Admin interface for QuestionEvent model — immutable event log."""
    list_display = ('id', 'attempt_display', 'quiz_question', 'event_type', 
                    'timestamp', 'time_on_q_secs')
    list_filter = ('event_type', 'attempt__quiz__status', 'attempt__quiz__exam_type', 'timestamp')
    search_fields = ('attempt__student__username', 'quiz_question__question__text')
    readonly_fields = ('attempt', 'quiz_question', 'event_type', 'timestamp', 
                      'time_on_q_secs', 'payload', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Event Information', {'fields': ('attempt', 'quiz_question')}),
        ('Event Details', {'fields': ('event_type', 'timestamp', 'time_on_q_secs')}),
        ('Payload', {'fields': ('payload',), 'classes': ('collapse',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-timestamp',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def attempt_display(self, obj):
        return f"{obj.attempt.student.username} — {obj.attempt.quiz.title}"
    attempt_display.short_description = 'Attempt'


@admin.register(SectionTimer)
class SectionTimerAdmin(admin.ModelAdmin):
    """Admin interface for SectionTimer model."""
    list_display = ('id', 'attempt_display', 'section', 'started_at', 
                    'time_used_secs', 'is_completed', 'created_at')
    list_filter = ('is_completed', 'attempt__quiz__status', 'attempt__quiz__exam_type', 'started_at')
    search_fields = ('attempt__student__username', 'section__name')
    readonly_fields = ('attempt', 'section', 'started_at', 'time_used_secs', 'is_completed',
                      'created_at', 'updated_at')
    
    fieldsets = (
        ('Timer Information', {'fields': ('attempt', 'section')}),
        ('Timing', {'fields': ('started_at', 'time_used_secs')}),
        ('Status', {'fields': ('is_completed',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    ordering = ('-created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def attempt_display(self, obj):
        return f"{obj.attempt.student.username} — {obj.attempt.quiz.title}"
    attempt_display.short_description = 'Attempt'
