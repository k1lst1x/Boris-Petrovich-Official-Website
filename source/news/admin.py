from django.contrib import admin
from django.utils import timezone
from .models import NewsPost, NewsCategory


@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    save_on_top = True


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "published_at", "created_at")
    list_editable = ("is_published",)
    list_filter = ("is_published", "category", "created_at", "published_at")
    search_fields = ("title", "slug", "preview_text", "body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-published_at", "-created_at")
    save_on_top = True

    fieldsets = (
        ("Основное", {"fields": ("title", "slug", "category", "cover_image")}),
        ("Контент", {"fields": ("preview_text", "body")}),
        ("Публикация", {"fields": ("is_published", "published_at")}),
        ("Служебное", {"fields": ("created_at", "updated_at")}),
    )

    actions = ["make_published", "make_unpublished", "set_published_now"]

    @admin.action(description="Опубликовать (если даты нет, поставить сейчас)")
    def make_published(self, request, queryset):
        for post in queryset:
            post.publish()
        self.message_user(request, "Выбранные публикации опубликованы.")

    @admin.action(description="Снять с публикации")
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)
        self.message_user(request, "Выбранные публикации сняты с публикации.")

    @admin.action(description="Поставить дату публикации = сейчас")
    def set_published_now(self, request, queryset):
        now = timezone.now()
        queryset.update(published_at=now)
        self.message_user(request, "Дата публикации обновлена на текущее время.")
