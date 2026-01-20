from django.db import models
from django.utils import timezone


class NewsCategory(models.Model):
    title = models.CharField("Название", max_length=120)
    slug = models.SlugField("Slug", unique=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Категория новостей"
        verbose_name_plural = "Категории новостей"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.title


class NewsPost(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Slug", unique=True)

    category = models.ForeignKey(
        NewsCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
        verbose_name="Категория",
    )

    preview_text = models.TextField("Краткое описание", blank=True)
    body = models.TextField("Текст статьи")

    cover_image = models.ImageField(
        "Обложка",
        upload_to="news/covers/",
        blank=True,
        null=True,
    )

    is_published = models.BooleanField("Опубликовано", default=False)
    published_at = models.DateTimeField("Дата публикации", blank=True, null=True)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "Новость / статья"
        verbose_name_plural = "Новости / статьи"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["published_at"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.title

    def publish(self):
        self.is_published = True
        if not self.published_at:
            self.published_at = timezone.now()
        self.save(update_fields=["is_published", "published_at"])

    def unpublish(self):
        self.is_published = False
        self.save(update_fields=["is_published"])
