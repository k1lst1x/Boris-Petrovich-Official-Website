import mimetypes
import os

from django.http import FileResponse, Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, render

from .models import Document, DocumentCategory


def _decorate_docs_for_user(docs, user):
    """
    Добавляем "виртуальные" поля на объект документа, чтобы шаблон мог
    корректно рисовать: скачать / оплатить / войти / закрыто.
    """
    user_is_auth = bool(user and getattr(user, "is_authenticated", False))

    for d in docs:
        d.user_can_access = d.can_user_access(user)
        d.user_needs_login = (d.is_paid and not user_is_auth)
        # locked_reason удобно для текста/бейджей
        if not d.is_published:
            d.locked_reason = "not_published"
        elif not d.is_open:
            d.locked_reason = "closed"
        elif d.access_type == d.AccessType.PAID and not d.user_can_access:
            d.locked_reason = "need_pay"
        else:
            d.locked_reason = None

    return docs


def document_list(request):
    docs = (
        Document.objects
        .filter(is_published=True)
        .select_related("category")
        .order_by("-created_at")
    )
    docs = _decorate_docs_for_user(docs, request.user)

    categories = DocumentCategory.objects.filter(is_active=True).order_by("order", "title")
    return render(request, "documents/document_list.html", {
        "docs": docs,
        "categories": categories,
        "current_category": None,
    })


def document_list_by_category(request, category_slug: str):
    category = get_object_or_404(DocumentCategory, slug=category_slug, is_active=True)

    docs = (
        category.documents
        .filter(is_published=True)
        .select_related("category")
        .order_by("-created_at")
    )
    docs = _decorate_docs_for_user(docs, request.user)

    categories = DocumentCategory.objects.filter(is_active=True).order_by("order", "title")
    return render(request, "documents/document_list.html", {
        "docs": docs,
        "categories": categories,
        "current_category": category,
    })


def document_detail(request, slug: str):
    doc = get_object_or_404(Document, slug=slug, is_published=True)
    can_access = doc.can_user_access(request.user)

    # те же удобные флаги, чтобы шаблон не гадал
    doc.user_can_access = can_access
    doc.user_needs_login = (doc.is_paid and not request.user.is_authenticated)

    return render(request, "documents/document_detail.html", {
        "doc": doc,
        "can_access": can_access,
    })


def document_pay_stub(request, slug: str):
    """
    Заглушка оплаты: позже сюда подключишь оплату/создание заказа.
    Пока просто показываем страницу с кнопкой "вернуться".
    """
    doc = get_object_or_404(Document, slug=slug, is_published=True)

    # если документ бесплатный, "оплата" не нужна
    if not doc.is_paid:
        return render(request, "documents/document_pay_stub.html", {
            "doc": doc,
            "message": "Этот документ бесплатный. Оплата не требуется.",
        })

    if not request.user.is_authenticated:
        return HttpResponseForbidden("Нужен вход в аккаунт для оплаты.")

    return render(request, "documents/document_pay_stub.html", {
        "doc": doc,
        "message": "Здесь будет оплата. Пока заглушка.",
    })


def document_download(request, slug: str):
    doc = get_object_or_404(Document, slug=slug, is_published=True)

    if not doc.can_user_access(request.user):
        if doc.is_paid and not request.user.is_authenticated:
            return HttpResponseForbidden("Нужен вход в аккаунт для доступа.")
        return HttpResponseForbidden("Доступ запрещён.")

    if not doc.file:
        raise Http404("Файл не найден.")

    file_path = doc.file.path
    if not os.path.exists(file_path):
        raise Http404("Файл не найден на сервере.")

    content_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(
        open(file_path, "rb"),
        content_type=content_type or "application/octet-stream",
    )
    filename = os.path.basename(file_path)
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response
