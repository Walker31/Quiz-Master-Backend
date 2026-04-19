from django.db import models
from django.conf import settings
from core.models import BaseModel
from apps.quiz.models import Quiz, QuizQuestion, QuizSection
from apps.content.models import QuestionOption


class QuizAttempt(BaseModel):
    """
    One sitting of a student attempting a quiz.
    Created when the student hits /start/; updated in real-time via heartbeat.
    Results (marks, rank) are populated when the student hits /submit/.
    """
    STATUS = [
        ('IN_PROGRESS', 'In Progress'),
        ('SUBMITTED',   'Submitted'),
        ('TIMED_OUT',   'Timed Out'),
        ('ABANDONED',   'Abandoned'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='attempts'
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='attempts'
    )
    attempt_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=12, choices=STATUS, default='IN_PROGRESS')

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    time_elapsed_secs = models.PositiveIntegerField(
        default=0, help_text="Updated via heartbeat every 30 seconds."
    )

    # Results — populated by AttemptEvaluator on submit
    total_marks = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    marks_obtained = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    correct_count = models.PositiveIntegerField(null=True)
    wrong_count = models.PositiveIntegerField(null=True)
    skipped_count = models.PositiveIntegerField(null=True)
    percentile = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    rank = models.PositiveIntegerField(null=True)
    is_passed = models.BooleanField(null=True)

    # Proctoring
    tab_switch_count = models.PositiveIntegerField(default=0)
    fullscreen_exits = models.PositiveIntegerField(default=0)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    class Meta:
        db_table = 'attempt_quiz_attempt'
        unique_together = ('student', 'quiz', 'attempt_number')
        ordering = ['-started_at']

    def __str__(self):
        return f"{self.student.username} — {self.quiz.title} #{self.attempt_number}"


class QuestionResponse(BaseModel):
    """
    Student's answer to one question within an attempt.
    Created as empty rows when the attempt starts; updated in real-time as the student answers.
    """
    VISIT_STATUS = [
        ('NOT_VISITED',      'Not Visited'),
        ('VISITED',          'Visited / Seen'),
        ('ANSWERED',         'Answered'),
        ('MARKED_REVIEW',    'Marked for Review'),
        ('ANSWERED_REVIEW',  'Answered + Marked for Review'),
    ]

    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name='responses'
    )
    quiz_question = models.ForeignKey(
        QuizQuestion, on_delete=models.CASCADE, related_name='responses'
    )
    visit_status = models.CharField(
        max_length=16, choices=VISIT_STATUS, default='NOT_VISITED'
    )

    # Answer (only one will be set depending on q_type)
    selected_options = models.ManyToManyField(
        QuestionOption, blank=True,
        help_text="For MCQ_SINGLE and MCQ_MULTI."
    )
    integer_answer = models.DecimalField(
        max_digits=10, decimal_places=4, null=True, blank=True,
        help_text="For INTEGER / FILL_BLANK question types."
    )
    text_answer = models.TextField(
        blank=True,
        help_text="For SUBJECTIVE question types."
    )

    # Per-question time tracking
    first_visited_at = models.DateTimeField(null=True, blank=True)
    last_answered_at = models.DateTimeField(null=True, blank=True)
    time_spent_secs = models.PositiveIntegerField(
        default=0, help_text="Cumulative seconds spent on this question."
    )

    # Evaluation — set by AttemptEvaluator
    is_correct = models.BooleanField(null=True)
    marks_awarded = models.DecimalField(max_digits=8, decimal_places=2, null=True)
    is_manually_graded = models.BooleanField(
        default=False, help_text="True for SUBJECTIVE; graded by an admin."
    )

    class Meta:
        db_table = 'attempt_question_response'
        unique_together = ('attempt', 'quiz_question')

    def __str__(self):
        return f"Attempt#{self.attempt_id} / Q#{self.quiz_question_id} [{self.visit_status}]"


class QuestionEvent(BaseModel):
    """
    Immutable event log — every student interaction timestamped.
    Never updated after creation; used for audit and analytics.
    """
    EVENT_TYPES = [
        ('VISIT',        'Question visited'),
        ('ANSWER',       'Answer selected/changed'),
        ('CLEAR',        'Answer cleared'),
        ('MARK_REVIEW',  'Marked for review'),
        ('UNMARK',       'Review unmarked'),
        ('LEAVE',        'Navigated away'),
    ]

    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name='events'
    )
    quiz_question = models.ForeignKey(
        QuizQuestion, on_delete=models.CASCADE, related_name='events'
    )
    event_type = models.CharField(max_length=12, choices=EVENT_TYPES)
    timestamp = models.DateTimeField(auto_now_add=True)
    time_on_q_secs = models.PositiveIntegerField(
        help_text="Seconds spent on this question before this event fired."
    )
    payload = models.JSONField(
        default=dict,
        help_text="Selected option ids, integer value, or other event data."
    )

    class Meta:
        db_table = 'attempt_question_event'
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['attempt', 'quiz_question', 'timestamp']),
        ]

    def __str__(self):
        return f"[{self.event_type}] Attempt#{self.attempt_id} Q#{self.quiz_question_id}"


class SectionTimer(BaseModel):
    """Tracks per-section time when sections have individual timers."""
    attempt = models.ForeignKey(
        QuizAttempt, on_delete=models.CASCADE, related_name='section_timers'
    )
    section = models.ForeignKey(
        QuizSection, on_delete=models.CASCADE, related_name='timers'
    )
    started_at = models.DateTimeField()
    time_used_secs = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)

    class Meta:
        db_table = 'attempt_section_timer'
        unique_together = ('attempt', 'section')

    def __str__(self):
        return f"Attempt#{self.attempt_id} / Section#{self.section_id} — {self.time_used_secs}s"
