from django.urls import path
from . import views
app_name = 'certificates'
urlpatterns = [
    path('',                             views.my_certificates,    name='list'),
    path('issue/<slug:course_slug>/',    views.issue_certificate,  name='issue'),
    path('download/<uuid:cert_id>/',     views.download_certificate,name='download'),
    path('verify/<uuid:cert_id>/',       views.verify_certificate, name='verify'),
]
