from django.contrib import admin
from .models import Certificate

@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student','course','grade','issued_at','cert_id']
    readonly_fields = ['cert_id','issued_at']
