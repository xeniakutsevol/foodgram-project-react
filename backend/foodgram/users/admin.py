from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_filter = ('email', 'username', 'is_superuser', 'is_staff',
                   'is_active')
