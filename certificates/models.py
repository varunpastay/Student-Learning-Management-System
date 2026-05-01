from django.db import models
from django.conf import settings
import uuid

class Certificate(models.Model):
    student    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates')
    course     = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='certificates')
    cert_id    = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    issued_at  = models.DateTimeField(auto_now_add=True)
    grade      = models.CharField(max_length=5, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"Certificate: {self.student.get_full_name()} — {self.course.title}"

    @property
    def verify_url(self):
        return f"/certificates/verify/{self.cert_id}/"
