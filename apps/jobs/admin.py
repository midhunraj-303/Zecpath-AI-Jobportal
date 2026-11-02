from django.contrib import admin
from .models import Job

# Register your models here.
@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    
    list_display = (
        'job_id',
        'job_title',
        'employer',
        'location',
        'is_active',
        'created_at'
    )

    list_filter = (
        'is_active',
        'employment_type',
        'location'
    )

    search_fields = (
        'job_title',
        'employer__company_name',
        'location'
    )
    