from django.urls import path
from . import views
app_name = 'forum'
urlpatterns = [
    path('course/<slug:course_slug>/',       views.forum_list,  name='list'),
    path('course/<slug:course_slug>/new/',   views.create_post, name='create'),
    path('post/<int:post_id>/',              views.post_detail, name='post'),
    path('reply/<int:reply_id>/answer/',     views.mark_answer, name='mark_answer'),
]
