from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Доп. информация", {"fields": ("full_name", "phone", "company")}),
    )

    list_display = ("username", "email", "full_name", "phone", "company", "is_staff", "is_active")
    search_fields = ("username", "email", "full_name", "phone", "company")
