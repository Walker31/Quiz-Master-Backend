from django.db import models
from django.conf import settings
from core.models import BaseModel


class ExamType(BaseModel):
    """Top-level exam category: JEE Main, JEE Advanced, GATE CS, NEET, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'content_exam_type'
        ordering = ['name']

    def __str__(self):
        return self.name


class Subject(BaseModel):
    """Subject within an exam type: Physics, Mathematics, Chemistry."""
    exam_type = models.ForeignKey(
        ExamType, on_delete=models.CASCADE, related_name='subjects'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, blank=True)  # PHY, MATH, CHEM
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'content_subject'
        ordering = ['exam_type', 'order', 'name']
        unique_together = ('exam_type', 'name')

    def __str__(self):
        return f"{self.exam_type.name} — {self.name}"


class Chapter(BaseModel):
    """Chapter within a subject: Mechanics, Algebra, Organic Chemistry."""
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name='chapters'
    )
    name = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'content_chapter'
        ordering = ['subject', 'order', 'name']
        unique_together = ('subject', 'name')

    def __str__(self):
        return f"{self.subject.name} / {self.name}"


class Tag(BaseModel):
    """Free-form tag for questions: 'PYQ-2023', 'High-Weightage', etc."""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        db_table = 'content_tag'
        ordering = ['name']

    def __str__(self):
        return self.name


class Question(BaseModel):
    """
    A single question in the question bank.
    Supports 5 question types; options are stored in QuestionOption.
    """
    QUESTION_TYPES = [
        ('MCQ_SINGLE',  'MCQ Single Correct'),
        ('MCQ_MULTI',   'MCQ Multiple Correct'),
        ('INTEGER',     'Integer / Numerical'),
        ('FILL_BLANK',  'Fill in the Blank'),
        ('SUBJECTIVE',  'Subjective'),
    ]
    DIFFICULTY = [
        ('EASY',   'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD',   'Hard'),
    ]

    chapter = models.ForeignKey(
        Chapter, on_delete=models.CASCADE, related_name='questions'
    )
    q_type = models.CharField(
        max_length=12, choices=QUESTION_TYPES, default='MCQ_SINGLE'
    )
    difficulty = models.CharField(
        max_length=6, choices=DIFFICULTY, default='MEDIUM'
    )

    # Content
    text = models.TextField(help_text="Supports LaTeX via KaTeX. Use $...$ for inline math.")
    image = models.ImageField(upload_to='questions/images/', blank=True)

    # Solution
    solution = models.TextField(blank=True)
    solution_video = models.URLField(blank=True)

    # Marking scheme (defaults; can be overridden per QuizQuestion)
    marks_correct = models.DecimalField(max_digits=5, decimal_places=2, default=4)
    marks_wrong = models.DecimalField(max_digits=5, decimal_places=2, default=-1)
    marks_partial = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text="Partial marks for MCQ_MULTI when some correct options are selected."
    )

    # Metadata
    tags = models.ManyToManyField(Tag, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name='created_questions'
    )
    is_verified = models.BooleanField(default=False)
    year = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="PYQ year if this is a previous year question."
    )

    class Meta:
        db_table = 'content_question'
        ordering = ['chapter', 'difficulty']
        indexes = [
            models.Index(fields=['chapter', 'difficulty']),
            models.Index(fields=['q_type', 'is_verified']),
        ]

    def __str__(self):
        return f"Q{self.id} [{self.get_q_type_display()}] — {self.chapter}"


class QuestionOption(BaseModel):
    """
    An answer option for a question.
    MCQ_SINGLE: exactly one is_correct=True.
    MCQ_MULTI: one or more is_correct=True.
    INTEGER/FILL_BLANK: one option with is_correct=True holds the correct value in `text`.
    """
    LABELS = [('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D'), ('E', 'E')]

    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='options'
    )
    label = models.CharField(max_length=1, choices=LABELS)
    text = models.TextField()
    image = models.ImageField(upload_to='questions/options/', blank=True)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'content_question_option'
        ordering = ['question', 'order']
        unique_together = ('question', 'label')

    def __str__(self):
        correct = "✓" if self.is_correct else " "
        return f"[{correct}] {self.question_id} / {self.label}: {self.text[:60]}"
