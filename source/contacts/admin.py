from django.contrib import admin
from .models import ContactProfile, ContactItem, ContactRequest


class ContactItemInline(admin.TabularInline):
    model = ContactItem
    extra = 1


@admin.register(ContactProfile)
class ContactProfileAdmin(admin.ModelAdmin):
    inlines = [ContactItemInline]
    list_display = ("title", "is_active", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("title", "about")


@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "phone", "created_at", "is_processed")
    list_filter = ("is_processed", "created_at")
    search_fields = ("full_name", "email", "phone", "message")
    readonly_fields = ("created_at",)
    actions = ["mark_processed"]

    def mark_processed(self, request, queryset):
        queryset.update(is_processed=True)

    mark_processed.short_description = "Отметить как обработанные"
