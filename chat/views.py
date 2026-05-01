"""chat/views.py"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import ChatRoom, ChatMessage
from courses.models import Course, Enrollment
from accounts.models import User


@login_required
def chat_list(request):
    """Show all chat rooms for current user."""
    user = request.user
    if user.is_student:
        rooms = ChatRoom.objects.filter(student=user).select_related('teacher','course').order_by('-created_at')
    else:
        rooms = ChatRoom.objects.filter(teacher=user).select_related('student','course').order_by('-created_at')

    # Add unread counts
    rooms_data = []
    for room in rooms:
        rooms_data.append({'room': room, 'unread': room.unread_count(user)})

    return render(request, 'chat/chat_list.html', {'rooms_data': rooms_data})


@login_required
def chat_room(request, room_id):
    room = get_object_or_404(ChatRoom, id=room_id)
    user = request.user

    # Permission check
    if user != room.student and user != room.teacher:
        messages.error(request, 'Access denied.')
        return redirect('chat:list')

    # Mark messages as read
    room.messages.filter(is_read=False).exclude(sender=user).update(is_read=True)

    chat_messages = room.messages.select_related('sender').all()

    if request.method == 'POST':
        text = request.POST.get('message', '').strip()
        if text:
            msg = ChatMessage.objects.create(room=room, sender=user, message=text)
            # Email the other user
            try:
                from notifications.email_utils import email_new_chat_message
                recipient = room.teacher if user.is_student else room.student
                email_new_chat_message(msg, recipient)
            except Exception: pass
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'ok', 'message': text,
                                     'sender': user.get_full_name(),
                                     'time': timezone.now().strftime('%H:%M')})
        return redirect('chat:room', room_id=room_id)

    return render(request, 'chat/chat_room.html', {
        'room': room, 'chat_messages': chat_messages,
        'other_user': room.teacher if user.is_student else room.student,
    })


@login_required
def start_chat(request, course_slug):
    """Student starts a chat with the course teacher."""
    course = get_object_or_404(Course, slug=course_slug)
    user = request.user

    if not user.is_student:
        messages.error(request, 'Only students can initiate chats.')
        return redirect('courses:detail', slug=course_slug)

    if not Enrollment.objects.filter(student=user, course=course, is_active=True).exists():
        messages.error(request, 'You must be enrolled to chat with the teacher.')
        return redirect('courses:detail', slug=course_slug)

    room, created = ChatRoom.objects.get_or_create(
        student=user, teacher=course.teacher, course=course
    )
    if created:
        ChatMessage.objects.create(
            room=room, sender=user,
            message=f'Hi! I have a question about {course.title}.'
        )
    return redirect('chat:room', room_id=room.id)


@login_required
def get_new_messages(request, room_id):
    """AJAX polling for new messages."""
    room = get_object_or_404(ChatRoom, id=room_id)
    if request.user != room.student and request.user != room.teacher:
        return JsonResponse({'error': 'forbidden'}, status=403)

    last_id = int(request.GET.get('last_id', 0))
    new_msgs = room.messages.filter(id__gt=last_id).select_related('sender')
    new_msgs.filter(is_read=False).exclude(sender=request.user).update(is_read=True)

    data = [{'id': m.id, 'sender': m.sender.get_full_name(),
             'message': m.message, 'time': m.sent_at.strftime('%H:%M'),
             'is_me': m.sender == request.user} for m in new_msgs]
    return JsonResponse({'messages': data})
