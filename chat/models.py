"""chat/models.py — Direct messaging between students and teachers."""
from django.db import models
from django.conf import settings


class ChatRoom(models.Model):
    """A private chat room between a student and teacher for a course."""
    student  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='student_rooms', limit_choices_to={'role':'student'})
    teacher  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                  related_name='teacher_rooms', limit_choices_to={'role':'teacher'})
    course   = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'teacher', 'course')

    def __str__(self):
        return f"{self.student.get_full_name()} ↔ {self.teacher.get_full_name()} [{self.course.title}]"

    @property
    def last_message(self):
        return self.messages.order_by('-sent_at').first()

    def unread_count(self, user):
        return self.messages.filter(is_read=False).exclude(sender=user).count()


class ChatMessage(models.Model):
    room     = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    message  = models.TextField()
    sent_at  = models.DateTimeField(auto_now_add=True)
    is_read  = models.BooleanField(default=False)

    class Meta:
        ordering = ['sent_at']

    def __str__(self):
        return f"{self.sender.get_full_name()}: {self.message[:50]}"
