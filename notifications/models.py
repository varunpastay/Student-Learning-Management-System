"""notifications/models.py"""
from django.db import models
from django.conf import settings


class Notification(models.Model):
    class Type(models.TextChoices):
        ASSIGNMENT = 'assignment', 'Assignment'
        COURSE     = 'course',     'Course'
        GRADE      = 'grade',      'Grade'
        SYSTEM     = 'system',     'System'

    user      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title     = models.CharField(max_length=200)
    message   = models.TextField()
    notification_type = models.CharField(max_length=15, choices=Type.choices, default=Type.SYSTEM)
    is_read   = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.title} ({'Read' if self.is_read else 'Unread'})"

    class Meta:
        ordering = ['-created_at']
