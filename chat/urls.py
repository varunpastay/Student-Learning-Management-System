from django.urls import path
from . import views
app_name = 'chat'
urlpatterns = [
    path('',                        views.chat_list,      name='list'),
    path('room/<int:room_id>/',     views.chat_room,      name='room'),
    path('start/<slug:course_slug>/', views.start_chat,   name='start'),
    path('poll/<int:room_id>/',     views.get_new_messages, name='poll'),
]
