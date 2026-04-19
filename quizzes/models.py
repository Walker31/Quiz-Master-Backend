from django.db import models
from django.conf import settings

class Subject(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Chapter(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='chapters')
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Quiz(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='quizzes')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='quizzes')
    quiz_title = models.CharField(max_length=150)
    date_of_quiz = models.DateTimeField()
    time_duration = models.IntegerField() # In minutes
    remarks = models.TextField(blank=True, null=True)
    is_live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.quiz_title

class Question(models.Model):
    DIFFICULTY_CHOICES = [
        (1, 'Very Easy'),
        (2, 'Easy'),
        (3, 'Medium-Easy'),
        (4, 'Medium'),
        (5, 'Medium-Hard'),
        (6, 'Hard'),
        (7, 'Very Hard'),
        (8, 'Extremely Hard'),
        (9, 'JEE Advanced Level'),
        (10, 'Expert Level'),
    ]
    
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='questions', null=True, blank=True)
    question_statement = models.TextField()
    option_1 = models.TextField()
    option_2 = models.TextField()
    option_3 = models.TextField()
    option_4 = models.TextField()
    correct_option = models.IntegerField() # 1, 2, 3, or 4
    difficulty_level = models.IntegerField(choices=DIFFICULTY_CHOICES, default=5)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['quiz', 'difficulty_level']
        indexes = [
            models.Index(fields=['subject', 'difficulty_level']),
            models.Index(fields=['chapter', 'difficulty_level']),
        ]

    def __str__(self):
        return f"{self.quiz.quiz_title} - Q{self.id} (Level {self.difficulty_level})"

class Score(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='scores')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scores')
    time_taken = models.IntegerField(blank=True, null=True) # In seconds
    max_marks = models.IntegerField()
    total_scored = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.quiz.quiz_title}"
