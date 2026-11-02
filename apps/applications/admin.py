from django.contrib import admin
from .models import Application
# Register your models here.

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'application_id',
        'candidate',
        'job',
        'status',
        'applied_at'
    )

    list_filter = (
        'status',
        'applied_at'
    )

    search_fields=(
        'candidate__full_name',
        'job__job_title'
    )

    
