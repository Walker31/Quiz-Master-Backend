from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel


class User(AbstractUser):
    """
    Custom user model with role-based access control.
    Roles: SUPERADMIN (platform owner), ADMIN (teacher/coach), STUDENT.
    """
    ROLES = [
        ('SUPERADMIN', 'Superadmin'),
        ('ADMIN', 'Admin'),
        ('STUDENT', 'Student'),
    ]
    role = models.CharField(max_length=12, choices=ROLES, default='STUDENT')
    phone = models.CharField(max_length=15, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    is_verified = models.BooleanField(default=False)

    class Meta:
        db_table = 'accounts_user'

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_admin(self):
        return self.role in ('ADMIN', 'SUPERADMIN')

    @property
    def is_superadmin(self):
        return self.role == 'SUPERADMIN'


class Batch(BaseModel):
    """
    A coaching class batch — groups students under an admin/teacher.
    Each batch is tied to a specific ExamType (e.g. JEE 2026).
    """
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True, null=True) # Adding null=True temporarily to make migration easy
    # exam_type FK added after content/ app is created (Phase 1.3)
    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='managed_batches',
        limit_choices_to={'role__in': ['ADMIN', 'SUPERADMIN']},
    )
    students = models.ManyToManyField(
        User,
        related_name='batches',
        blank=True,
        limit_choices_to={'role': 'STUDENT'},
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'accounts_batch'

    def __str__(self):
        return self.name
