from django.contrib import admin
from django.utils import timezone

from .models import Document, DocumentCategory, DocumentPurchase


@admin.register(DocumentCategory)
class DocumentCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "access_type",
        "price",
        "currency",
        "is_open",
        "is_published",
        "created_at",
    )
    list_filter = ("access_type", "is_open", "is_published", "category", "created_at")
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основное", {
            "fields": ("title", "slug", "description", "category", "preview_image")
        }),
        ("Файл", {
            "fields": ("file",)
        }),
        ("Доступ", {
            "fields": ("access_type", ("price", "currency"), "is_open", "is_published")
        }),
        ("Системное", {
            "fields": ("created_at", "updated_at")
        }),
    )

    ordering = ("-created_at",)
    actions = ["make_published", "make_unpublished", "make_open", "make_closed"]

    @admin.action(description="Опубликовать")
    def make_published(self, request, queryset):
        queryset.update(is_published=True)

    @admin.action(description="Снять с публикации")
    def make_unpublished(self, request, queryset):
        queryset.update(is_published=False)

    @admin.action(description="Открыть доступ")
    def make_open(self, request, queryset):
        queryset.update(is_open=True)

    @admin.action(description="Закрыть доступ")
    def make_closed(self, request, queryset):
        queryset.update(is_open=False)


@admin.register(DocumentPurchase)
class DocumentPurchaseAdmin(admin.ModelAdmin):
    list_display = ("user", "document", "status", "created_at", "paid_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email", "document__title", "document__slug")
    readonly_fields = ("created_at", "paid_at")
    ordering = ("-created_at",)

    actions = ["mark_as_paid", "mark_as_canceled", "mark_as_pending"]

    @admin.action(description="Пометить как оплачено")
    def mark_as_paid(self, request, queryset):
        now = timezone.now()
        queryset.update(status=DocumentPurchase.Status.PAID, paid_at=now)

    @admin.action(description="Пометить как отменено")
    def mark_as_canceled(self, request, queryset):
        queryset.update(status=DocumentPurchase.Status.CANCELED)

    @admin.action(description="Пометить как ожидание оплаты")
    def mark_as_pending(self, request, queryset):
        queryset.update(status=DocumentPurchase.Status.PENDING)
