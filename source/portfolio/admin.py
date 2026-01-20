from django.contrib import admin
from django.utils.html import format_html

from .models import (
    PortfolioPage,
    Case,
    CaseImage,
    CaseAttachment,
    CaseDocument,
)


class CaseImageInline(admin.TabularInline):
    model = CaseImage
    extra = 0
    fields = ("image", "thumb", "caption", "order", "is_active")
    readonly_fields = ("thumb",)
    ordering = ("order", "id")

    @admin.display(description="Превью")
    def thumb(self, obj: CaseImage):
        if not obj.image:
            return "—"
        return format_html(
            '<img src="{}" style="width:70px;height:48px;object-fit:cover;border-radius:8px;border:1px solid rgba(15,23,42,.12);" />',
            obj.image.url
        )


class CaseAttachmentInline(admin.TabularInline):
    model = CaseAttachment
    extra = 0
    fields = ("title", "file", "order", "is_active")
    ordering = ("order", "id")


class CaseDocumentInline(admin.TabularInline):
    """
    Привязка документов к кейсу.
    """
    model = CaseDocument
    extra = 0
    fields = ("document", "title_override", "order", "is_active")
    ordering = ("order", "id")
    autocomplete_fields = ("document",)


@admin.register(PortfolioPage)
class PortfolioPageAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "order", "is_published")
    list_editable = ("order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("order", "title")
    save_on_top = True


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at", "cover_thumb")
    list_editable = ("is_published",)
    list_filter = ("is_published", "created_at")
    search_fields = ("title", "slug", "short_text", "body")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "cover_thumb_big")
    ordering = ("-created_at",)
    save_on_top = True

    filter_horizontal = ("pages",)

    inlines = (CaseImageInline, CaseAttachmentInline, CaseDocumentInline)

    fieldsets = (
        ("Основное", {
            "fields": ("title", "slug", "pages", "cover_image", "cover_thumb_big")
        }),
        ("Описание", {
            "fields": ("short_text", "body")
        }),
        ("Публикация", {
            "fields": ("is_published",)
        }),
        ("Служебное", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.display(description="Обложка")
    def cover_thumb(self, obj: Case):
        if not obj.cover_image:
            return "—"
        return format_html(
            '<img src="{}" style="width:52px;height:36px;object-fit:cover;border-radius:8px;border:1px solid rgba(15,23,42,.12);" />',
            obj.cover_image.url
        )

    @admin.display(description="Превью")
    def cover_thumb_big(self, obj: Case):
        if not obj.cover_image:
            return "—"
        return format_html(
            '<img src="{}" style="max-width:360px;width:100%;height:auto;border-radius:14px;border:1px solid rgba(15,23,42,.12);" />',
            obj.cover_image.url
        )


@admin.register(CaseDocument)
class CaseDocumentAdmin(admin.ModelAdmin):
    """
    Не обязательно, но удобно: видеть все связи кейс-документ в одном месте.
    """
    list_display = ("case", "document", "order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("case__title", "case__slug", "document__title", "document__slug")
    ordering = ("case", "order", "id")
    autocomplete_fields = ("case", "document")
