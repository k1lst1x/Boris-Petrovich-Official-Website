from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    # Переопределяем email из AbstractUser, чтобы сделать уникальным
    email = models.EmailField("Почта", unique=True)

    full_name = models.CharField("ФИО", max_length=255, blank=True)
    phone = models.CharField("Телефон", max_length=32, blank=True)
    company = models.CharField("Компания", max_length=255, blank=True)

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self) -> str:
        return self.username
