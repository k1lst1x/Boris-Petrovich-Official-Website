from django.db import models


class Recommendation(models.Model):
    title = models.CharField("Название", max_length=255)
    document = models.FileField("Документ", upload_to="recommendations/")
    order = models.PositiveIntegerField("Порядок", default=0)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    edited_at = models.DateTimeField("Изменено", auto_now=True)

    class Meta:
        ordering = ["order", "-created_at"]
        verbose_name = "Рекомендация"
        verbose_name_plural = "Рекомендации"

    def __str__(self):
        return self.title
