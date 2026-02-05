from django.contrib import admin
from .models import Recommendation


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "created_at", "edited_at")
    list_editable = ("order",)
    search_fields = ("title",)
    ordering = ("order", "-created_at")
