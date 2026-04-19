from django.db import models
from django.db.models import Q
from django.conf import settings
from core.models import BaseModel
from apps.content.models import ExamType, Subject, Question


class Quiz(BaseModel):
    """
    A quiz (test / mock exam) created by an admin.
    Can be open, assigned to specific students, or restricted to a batch.
    """
    STATUS = [
        ('DRAFT',     'Draft'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED',  'Archived'),
    ]
    ACCESS = [
        ('OPEN',     'Open to all'),
        ('ASSIGNED', 'Assigned only'),
        ('BATCH',    'Batch'),
    ]
    SOLUTION_RELEASE = [
        ('SUBMIT',   'After submit'),
        ('END_TIME', 'After end time'),
        ('NEVER',    'Never'),
    ]

    title = models.CharField(max_length=300)
    exam_type = models.ForeignKey(
        ExamType, on_delete=models.SET_NULL, null=True, related_name='quizzes'
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_quizzes'
    )

    # Status & access
    status = models.CharField(max_length=10, choices=STATUS, default='DRAFT')
    access_type = models.CharField(max_length=10, choices=ACCESS, default='OPEN')

    # Scheduling
    start_time = models.DateTimeField(
        null=True, blank=True, help_text="Leave blank for always-open quiz."
    )
    end_time = models.DateTimeField(null=True, blank=True)
    duration_mins = models.PositiveIntegerField(help_text="Total exam duration in minutes.")

    # Behaviour
    shuffle_questions = models.BooleanField(default=False)
    shuffle_options = models.BooleanField(default=False)
    show_solution_after = models.CharField(
        max_length=10, choices=SOLUTION_RELEASE, default='SUBMIT'
    )
    max_attempts = models.PositiveIntegerField(default=1)
    pass_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=35.0)

    instructions = models.TextField(blank=True)
    is_proctored = models.BooleanField(
        default=False, help_text="Enable tab-switch and fullscreen monitoring."
    )

    class Meta:
        db_table = 'quiz_quiz'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.title}"


class QuizSection(BaseModel):
    """
    A section within a quiz, typically one per subject (Physics / Chemistry / Math).
    Sections can have their own per-section timer.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='sections')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quiz_sections')
    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)
    duration_mins = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Per-section timer. If null, uses the quiz-level timer."
    )
    max_questions = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="If set, students can only attempt this many questions in the section."
    )

    class Meta:
        db_table = 'quiz_section'
        ordering = ['quiz', 'order']
        unique_together = ('quiz', 'name')

    def __str__(self):
        return f"{self.quiz.title} / {self.name}"


class QuizQuestion(BaseModel):
    """
    Links a Question into a QuizSection, with optional per-quiz mark overrides.
    """
    section = models.ForeignKey(
        QuizSection, on_delete=models.CASCADE, related_name='quiz_questions'
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='quiz_questions'
    )
    order = models.PositiveIntegerField(default=0)

    # Override the question's default marks for this specific quiz
    marks_correct = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Overrides Question.marks_correct if set."
    )
    marks_wrong = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Overrides Question.marks_wrong if set."
    )

    class Meta:
        db_table = 'quiz_question'
        ordering = ['section', 'order']
        unique_together = ('section', 'question')

    def __str__(self):
        return f"{self.section} — Q{self.question_id}"

    def effective_marks_correct(self):
        return self.marks_correct if self.marks_correct is not None \
               else self.question.marks_correct

    def effective_marks_wrong(self):
        return self.marks_wrong if self.marks_wrong is not None \
               else self.question.marks_wrong


class QuizAssignment(BaseModel):
    """
    Assigns a quiz to a specific student or an entire batch.
    Exactly one of assigned_to or batch must be set.
    """
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='assignments')
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='quiz_assignments'
    )
    batch = models.ForeignKey(
        'accounts.Batch', on_delete=models.CASCADE,
        null=True, blank=True, related_name='quiz_assignments'
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='issued_assignments'
    )
    deadline = models.DateTimeField(null=True, blank=True)
    is_mandatory = models.BooleanField(default=False)

    class Meta:
        db_table = 'quiz_assignment'
        constraints = [
            models.CheckConstraint(
                condition=Q(assigned_to__isnull=False) | Q(batch__isnull=False),
                name='assignment_has_target',
            )
        ]

    def __str__(self):
        target = self.assigned_to or self.batch
        return f"{self.quiz.title} → {target}"
