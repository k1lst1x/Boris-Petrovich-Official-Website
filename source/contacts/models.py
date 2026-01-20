from django.db import models


class ContactProfile(models.Model):
    title = models.CharField("Заголовок", max_length=120, default="Контакты")
    about = models.TextField("О нас / описание", blank=True)
    is_active = models.BooleanField("Активный профиль", default=True)

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        verbose_name = "Профиль контактов"
        verbose_name_plural = "Профили контактов"

    def __str__(self) -> str:
        return self.title


class ContactItem(models.Model):
    class Kind(models.TextChoices):
        PHONE = "phone", "Телефон"
        EMAIL = "email", "Email"
        WHATSAPP = "whatsapp", "WhatsApp"
        TELEGRAM = "telegram", "Telegram"
        ADDRESS = "address", "Адрес"
        WEBSITE = "website", "Сайт"
        OTHER = "other", "Другое"

    profile = models.ForeignKey(
        ContactProfile,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Профиль",
    )

    kind = models.CharField("Тип", max_length=20, choices=Kind.choices)
    label = models.CharField("Подпись", max_length=120, blank=True)
    value = models.CharField("Значение", max_length=255)
    link = models.CharField("Ссылка", max_length=255, blank=True)
    is_active = models.BooleanField("Показывать", default=True)
    order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self) -> str:
        return f"{self.get_kind_display()}: {self.value}"


class ContactRequest(models.Model):
    full_name = models.CharField("ФИО", max_length=255)
    email = models.EmailField("Email")
    phone = models.CharField("Телефон", max_length=64)
    message = models.TextField("Сообщение")

    created_at = models.DateTimeField("Создано", auto_now_add=True)
    is_processed = models.BooleanField("Обработано", default=False)

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} ({self.email})"
