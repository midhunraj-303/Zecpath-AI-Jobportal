from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Register your models here.

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'user_id',
        'username',
        'email',
        'phone',
        'role',
        'is_active',
        'is_verified',
        'is_staff',
    )

    list_filter = (
        'role',
        'is_active',
        'is_verified',
        'is_staff',
    )

    search_fields = (
        'username',
        'email',
        'phone',
    )

    ordering = ('user_id',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'Additional Information', {
                'fields' : (
                    'phone',
                    'role',
                    'is_verified',
                    'created_at',
                    'updated_at'
                )
            }
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Additional Information', {
                'fields' : (
                    'email',
                    'phone',
                    'role',
                    'is_verified',
                )
            }
        ),
    )

    readonly_fields = (
        'created_at',
        'updated_at'
    )

