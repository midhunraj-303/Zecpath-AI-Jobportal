from django.contrib import admin
from .models import Candidate

# Register your models here.

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):

    list_display=(
        'candidate_id',
        'user',
        'full_name',
        'location',
        'created_at'
    )

    search_fields=(
        'full_name',
        'user__username',
        'user__email'
    )
    