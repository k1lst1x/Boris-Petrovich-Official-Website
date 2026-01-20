from django.db import models


class PortfolioPage(models.Model):
    """
    Страница/раздел портфолио: например
    - "Энергоаудит"
    - "Экспертизы"
    - "Проектирование"
    """
    title = models.CharField("Название", max_length=160)
    slug = models.SlugField("Slug", unique=True)
    description = models.TextField("Описание", blank=True)

    order = models.PositiveIntegerField("Порядок", default=0)
    is_published = models.BooleanField("Опубликована", default=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Страница портфолио"
        verbose_name_plural = "Страницы портфолио"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self) -> str:
        return self.title


class Case(models.Model):
    title = models.CharField("Заголовок", max_length=200)
    slug = models.SlugField("Slug", unique=True)

    pages = models.ManyToManyField(
        PortfolioPage,
        blank=True,
        related_name="cases",
        verbose_name="Страницы портфолио",
    )

    cover_image = models.ImageField(
        "Обложка",
        upload_to="portfolio/cases/covers/",
        blank=True,
        null=True,
    )

    short_text = models.TextField("Короткое описание", blank=True)
    body = models.TextField("Текст кейса", blank=True)

    # Документы, привязанные к кейсу (из приложения documents)
    documents = models.ManyToManyField(
        "documents.Document",
        through="CaseDocument",
        blank=True,
        related_name="cases",
        verbose_name="Документы",
    )

    is_published = models.BooleanField("Опубликован", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Кейс"
        verbose_name_plural = "Кейсы"
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["is_published"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self) -> str:
        return self.title


class CaseDocument(models.Model):
    """
    Привязка документа к кейсу с сортировкой и опциональным названием.
    """
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="case_documents",
        verbose_name="Кейс",
    )
    document = models.ForeignKey(
        "documents.Document",
        on_delete=models.CASCADE,
        related_name="case_documents",
        verbose_name="Документ",
    )

    order = models.PositiveIntegerField("Порядок", default=0)
    title_override = models.CharField("Название в кейсе", max_length=200, blank=True)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        unique_together = ("case", "document")
        verbose_name = "Документ в кейсе"
        verbose_name_plural = "Документы в кейсах"
        indexes = [
            models.Index(fields=["order"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self) -> str:
        return f"{self.case} -> {self.document}"


class CaseImage(models.Model):
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Кейс",
    )

    image = models.ImageField("Фото", upload_to="portfolio/cases/images/")
    caption = models.CharField("Подпись", max_length=200, blank=True)

    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Фото кейса"
        verbose_name_plural = "Фото кейса"

    def __str__(self) -> str:
        return f"{self.case}: фото #{self.id}"


class CaseAttachment(models.Model):
    """
    Любые прикрепления к кейсу: PDF, DOCX, XLSX, картинки, архивы и т.д.
    """
    case = models.ForeignKey(
        Case,
        on_delete=models.CASCADE,
        related_name="attachments",
        verbose_name="Кейс",
    )

    title = models.CharField("Название", max_length=200)
    file = models.FileField("Файл", upload_to="portfolio/cases/attachments/")

    order = models.PositiveIntegerField("Порядок", default=0)
    is_active = models.BooleanField("Показывать", default=True)

    class Meta:
        ordering = ["order", "id"]
        verbose_name = "Файл кейса"
        verbose_name_plural = "Файлы кейса"

    def __str__(self) -> str:
        return f"{self.case}: {self.title}"
