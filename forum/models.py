"""forum/models.py — Per-course Q&A discussion board."""
from django.db import models
from django.conf import settings


class ForumPost(models.Model):
    course    = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name='forum_posts')
    author    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_posts')
    title     = models.CharField(max_length=200)
    body      = models.TextField()
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta: ordering = ['-is_pinned', '-created_at']

    def __str__(self): return self.title

    @property
    def reply_count(self): return self.replies.count()


class ForumReply(models.Model):
    post      = models.ForeignKey(ForumPost, on_delete=models.CASCADE, related_name='replies')
    author    = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='forum_replies')
    body      = models.TextField()
    is_answer = models.BooleanField(default=False, help_text='Mark as accepted answer')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta: ordering = ['-is_answer', 'created_at']

    def __str__(self): return f"Reply to: {self.post.title}"
