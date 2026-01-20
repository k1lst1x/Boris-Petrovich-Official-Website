from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class DocumentCategory(models.Model):
    title = models.CharField("Название", max_length=120)
    slug = models.SlugField("Slug", unique=True)
    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Активна", default=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Категория документов"
        verbose_name_plural = "Категории документов"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.title


class Document(models.Model):
    class AccessType(models.TextChoices):
        FREE = "free", "Бесплатно"
        PAID = "paid", "Платно"

    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Slug", unique=True)
    description = models.TextField("Описание", blank=True)

    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
        verbose_name="Категория",
    )

    file = models.FileField("Файл", upload_to="documents/")
    preview_image = models.ImageField(
        "Превью (опционально)",
        upload_to="documents/previews/",
        blank=True,
        null=True,
    )

    is_published = models.BooleanField("Опубликован", default=True)
    is_open = models.BooleanField("Открыт (доступ разрешён)", default=True)

    access_type = models.CharField(
        "Доступ",
        max_length=10,
        choices=AccessType.choices,
        default=AccessType.FREE,
    )
    price = models.DecimalField("Цена", max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField("Валюта", max_length=10, default="KZT")

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published", "is_open"]),
            models.Index(fields=["access_type"]),
            models.Index(fields=["created_at"]),
        ]
    
    @property
    def is_available(self) -> bool:
        return self.is_published and self.is_open    

    def __str__(self) -> str:
        return self.title

    def clean(self):
        # Если документ платный, цена должна быть
        if self.access_type == self.AccessType.PAID and (self.price is None):
            raise ValidationError({"price": "Для платного документа нужно указать цену."})

        # Если документ бесплатный, цену можно не хранить (не обязательно, но логично)
        # Если хочешь жёстко чистить:
        # if self.access_type == self.AccessType.FREE:
        #     self.price = None

    @property
    def is_paid(self) -> bool:
        return self.access_type == self.AccessType.PAID

    def can_user_access(self, user) -> bool:
        """
        Правило доступа:
        - если не опубликован или закрыт => никому
        - FREE => всем
        - PAID => только staff/superuser или оплатившим
        """
        if not self.is_published or not self.is_open:
            return False

        if self.access_type == self.AccessType.FREE:
            return True

        if user and getattr(user, "is_authenticated", False):
            if getattr(user, "is_staff", False) or getattr(user, "is_superuser", False):
                return True

            return DocumentPurchase.objects.filter(
                user=user,
                document=self,
                status=DocumentPurchase.Status.PAID,
            ).exists()

        return False


class DocumentPurchase(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает оплату"
        PAID = "paid", "Оплачено"
        CANCELED = "canceled", "Отменено"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="document_purchases",
        verbose_name="Пользователь",
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name="purchases",
        verbose_name="Документ",
    )

    status = models.CharField("Статус", max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    paid_at = models.DateTimeField("Оплачено", null=True, blank=True)

    class Meta:
        unique_together = ("user", "document")
        ordering = ["-created_at"]
        verbose_name = "Покупка документа"
        verbose_name_plural = "Покупки документов"
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["paid_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.user} -> {self.document} ({self.status})"

    def mark_paid(self):
        self.status = self.Status.PAID
        self.paid_at = timezone.now()
        self.save(update_fields=["status", "paid_at"])
