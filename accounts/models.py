"""
accounts/models.py
Custom User model with roles + extended profiles.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = 'student', 'Student'
        TEACHER = 'teacher', 'Teacher'
        ADMIN   = 'admin',   'Admin'

    role   = models.CharField(max_length=10, choices=Role.choices, default=Role.STUDENT)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio    = models.TextField(blank=True)
    phone  = models.CharField(max_length=20, blank=True)

    # ── Role helpers ───────────────────────────────────────────────────────────
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    class Meta:
        ordering = ['-date_joined']


class StudentProfile(models.Model):
    user         = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id   = models.CharField(max_length=20, unique=True, blank=True)
    department   = models.CharField(max_length=100, blank=True)
    year_of_study = models.PositiveIntegerField(default=1)
    cgpa         = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    date_of_birth = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Student Profile: {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.student_id:
            self.student_id = f"STU{self.user.id:05d}"
        super().save(*args, **kwargs)


class TeacherProfile(models.Model):
    user            = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    employee_id     = models.CharField(max_length=20, unique=True, blank=True)
    department      = models.CharField(max_length=100, blank=True)
    specialization  = models.CharField(max_length=200, blank=True)
    qualification   = models.CharField(max_length=200, blank=True)
    years_experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Teacher Profile: {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.employee_id:
            self.employee_id = f"TCH{self.user.id:05d}"
        super().save(*args, **kwargs)
