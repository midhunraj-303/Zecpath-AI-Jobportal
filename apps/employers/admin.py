from django.contrib import admin
from .models import Employer


@admin.register(Employer)
class EmployerAdmin(admin.ModelAdmin):

    list_display = (
        'employer_id',
        'user',
        'company_name',
        'location',
        'created_at'
    )

    search_fields = (
        'company_name',
        'user__username',
        'user__email'
    )

