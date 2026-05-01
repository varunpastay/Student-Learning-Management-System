"""feedback/models.py — Student ratings & feedback for teachers/courses."""
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class TeacherFeedback(models.Model):
    student  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='given_feedback', limit_choices_to={'role':'student'})
    teacher  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='received_feedback', limit_choices_to={'role':'teacher'})
    course   = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='feedback')
    rating   = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment  = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'teacher', 'course')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.get_full_name()} → {self.teacher.get_full_name()} ({self.rating}★)"

    @property
    def stars(self):
        return '★' * self.rating + '☆' * (5 - self.rating)
