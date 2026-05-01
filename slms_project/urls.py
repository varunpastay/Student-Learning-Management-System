from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls')),
    path('assignments/', include('assignments.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('api/v1/', include('api.urls')),
    path('feedback/', include('feedback.urls')),
    path('quiz/', include('quiz.urls')),
    path('certificates/', include('certificates.urls')),
    path('forum/', include('forum.urls')),
    # path('auth/', include('allauth.urls')),  # Enable when using PostgreSQL
    path('chat/', include('chat.urls')),
    path('chatbot/', include('chatbot.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('', lambda request: __import__('django.shortcuts', fromlist=['redirect']).redirect('/dashboard/')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
