from django.contrib import admin
from .models import ForumPost, ForumReply

class ReplyInline(admin.TabularInline):
    model = ForumReply; extra = 0

@admin.register(ForumPost)
class ForumPostAdmin(admin.ModelAdmin):
    list_display = ['title','course','author','reply_count','is_pinned','created_at']
    inlines = [ReplyInline]
