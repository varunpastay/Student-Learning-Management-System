"""
assignments/models.py
Assignment + Submission with file validation, late penalty, status tracking.
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
import os


def validate_file_extension(value):
    allowed = getattr(settings, 'ALLOWED_ASSIGNMENT_EXTENSIONS', ['.pdf', '.docx', '.doc', '.zip', '.txt'])
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed:
        raise ValidationError(f'Unsupported file type {ext}. Allowed: {", ".join(allowed)}')


def validate_file_size(value):
    max_size = getattr(settings, 'MAX_UPLOAD_SIZE', 10 * 1024 * 1024)
    if value.size > max_size:
        raise ValidationError(f'File too large. Maximum size is {max_size // (1024*1024)} MB.')


class Assignment(models.Model):
    course       = models.ForeignKey(
        'courses.Course', on_delete=models.CASCADE, related_name='assignments'
    )
    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_assignments', limit_choices_to={'role': 'teacher'}
    )
    title        = models.CharField(max_length=200)
    description  = models.TextField()
    deadline     = models.DateTimeField()
    total_marks  = models.PositiveIntegerField(default=100)
    allow_late   = models.BooleanField(default=False, help_text='Allow submissions after deadline')
    late_penalty = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
        help_text='Percentage deducted per day late (e.g. 5 = 5% per day)'
    )
    attachment   = models.FileField(
        upload_to='assignment_attachments/', blank=True, null=True,
        validators=[validate_file_extension, validate_file_size]
    )
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    @property
    def is_past_deadline(self):
        return timezone.now() > self.deadline

    @property
    def days_remaining(self):
        delta = self.deadline - timezone.now()
        return max(0, delta.days)

    def __str__(self):
        return f"{self.title} — {self.course.title}"

    class Meta:
        ordering = ['deadline']


class Submission(models.Model):
    class Status(models.TextChoices):
        PENDING   = 'pending',   'Pending'
        SUBMITTED = 'submitted', 'Submitted'
        LATE      = 'late',      'Late'
        GRADED    = 'graded',    'Graded'

    assignment   = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='submissions', limit_choices_to={'role': 'student'}
    )
    file         = models.FileField(
        upload_to='submissions/',
        validators=[validate_file_extension, validate_file_size]
    )
    notes        = models.TextField(blank=True, help_text='Optional notes for the teacher')
    status       = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Grading
    marks_obtained = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    feedback       = models.TextField(blank=True)
    graded_at      = models.DateTimeField(null=True, blank=True)
    graded_by      = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='graded_submissions'
    )

    @property
    def effective_marks(self):
        """Apply late penalty if submission was late."""
        if self.marks_obtained is None:
            return None
        if self.status == self.Status.LATE and self.assignment.late_penalty:
            days_late = max(0, (self.submitted_at - self.assignment.deadline).days)
            penalty = float(self.marks_obtained) * float(self.assignment.late_penalty) / 100 * days_late
            return round(max(0, float(self.marks_obtained) - penalty), 2)
        return float(self.marks_obtained)

    @property
    def percentage(self):
        if self.marks_obtained is None:
            return None
        return round((float(self.marks_obtained) / self.assignment.total_marks) * 100, 1)

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.assignment.title} ({self.status})"

    class Meta:
        unique_together = ('assignment', 'student')
        ordering = ['-submitted_at']
