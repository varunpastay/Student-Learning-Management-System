from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ForumPost, ForumReply
from courses.models import Course, Enrollment


@login_required
def forum_list(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    is_enrolled = Enrollment.objects.filter(student=request.user, course=course, is_active=True).exists() if request.user.is_student else True
    posts = ForumPost.objects.filter(course=course).select_related('author').prefetch_related('replies')
    return render(request, 'forum/forum_list.html', {'course':course,'posts':posts,'is_enrolled':is_enrolled})


@login_required
def post_detail(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    if request.method == 'POST' and 'reply' in request.POST:
        body = request.POST.get('body','').strip()
        if body:
            reply = ForumReply.objects.create(post=post, author=request.user, body=body)
            from notifications.email_utils import email_forum_reply
            email_forum_reply(reply)
            messages.success(request, 'Reply posted!')
        return redirect('forum:post', post_id=post_id)
    replies = post.replies.select_related('author').all()
    return render(request, 'forum/post_detail.html', {'post':post,'replies':replies})


@login_required
def create_post(request, course_slug):
    course = get_object_or_404(Course, slug=course_slug)
    if request.method == 'POST':
        title = request.POST.get('title','').strip()
        body  = request.POST.get('body','').strip()
        if title and body:
            ForumPost.objects.create(course=course, author=request.user, title=title, body=body)
            messages.success(request, 'Post created!')
        return redirect('forum:list', course_slug=course_slug)
    return render(request, 'forum/create_post.html', {'course':course})


@login_required
def mark_answer(request, reply_id):
    reply = get_object_or_404(ForumReply, id=reply_id, post__course__teacher=request.user)
    reply.is_answer = not reply.is_answer
    reply.save()
    return redirect('forum:post', post_id=reply.post_id)
