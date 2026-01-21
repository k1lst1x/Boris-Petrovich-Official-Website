import mimetypes
import os

from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import Document, DocumentCategory, DocumentPurchase


def _decorate_docs_for_user(docs, user, request_path: str = ""):
    """
    Добавляем "виртуальные" поля на объект документа, чтобы шаблон мог
    корректно рисовать: скачать / оплатить / войти / закрыто.
    """
    user_is_auth = bool(user and getattr(user, "is_authenticated", False))

    for d in docs:
        d.user_can_access = d.can_user_access(user)
        d.user_needs_login = (d.is_paid and not user_is_auth)

        # куда вести "Войти", чтобы вернуться назад
        if request_path:
            d.login_url_with_next = f"{reverse('login')}?next={request_path}"
        else:
            d.login_url_with_next = reverse("login")

        if not d.is_published:
            d.locked_reason = "not_published"
        elif not d.is_open:
            d.locked_reason = "closed"
        elif d.is_paid and not d.user_can_access:
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
    docs = _decorate_docs_for_user(docs, request.user, request.path)

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
    docs = _decorate_docs_for_user(docs, request.user, request.path)

    categories = DocumentCategory.objects.filter(is_active=True).order_by("order", "title")
    return render(request, "documents/document_list.html", {
        "docs": docs,
        "categories": categories,
        "current_category": category,
    })


def document_detail(request, slug: str):
    doc = get_object_or_404(Document, slug=slug, is_published=True)

    can_access = doc.can_user_access(request.user)

    doc.user_can_access = can_access
    doc.user_needs_login = (doc.is_paid and not request.user.is_authenticated)
    login_url_with_next = f"{reverse('login')}?next={request.path}"

    return render(request, "documents/document_detail.html", {
        "doc": doc,
        "can_access": can_access,
        "login_url_with_next": login_url_with_next,
    })


@login_required
def document_pay_stub(request, slug: str):
    """
    Заглушка оплаты: позже сюда подключишь оплату/создание заказа.
    Сейчас делаем хотя бы "покупку" в pending.
    """
    doc = get_object_or_404(Document, slug=slug, is_published=True)

    if not doc.is_open:
        raise Http404("Документ закрыт.")

    # если документ бесплатный, "оплата" не нужна
    if not doc.is_paid:
        return redirect("documents:detail", slug=doc.slug)

    purchase, _ = DocumentPurchase.objects.get_or_create(
        user=request.user,
        document=doc,
    )

    # оставляем pending, пока не прикрутили платежку
    if purchase.status != DocumentPurchase.Status.PAID:
        purchase.status = DocumentPurchase.Status.PENDING
        purchase.save(update_fields=["status"])

    return render(request, "documents/document_pay_stub.html", {
        "doc": doc,
        "purchase": purchase,
        "message": "Здесь будет оплата. Пока заглушка (статус: ожидает оплату).",
    })


def document_download(request, slug: str):
    doc = get_object_or_404(Document, slug=slug, is_published=True)

    # закрыт = не отдаём никому
    if not doc.is_open:
        raise Http404("Документ закрыт.")

    # если платный и не залогинен -> на login с next
    if doc.is_paid and not request.user.is_authenticated:
        return redirect(f"{reverse('login')}?next={request.path}")

    # если нет доступа (не купил) -> на оплату
    if not doc.can_user_access(request.user):
        if doc.is_paid:
            return redirect("documents:pay", slug=doc.slug)
        raise Http404("Доступ запрещён.")

    if not doc.file:
        raise Http404("Файл не найден.")

    file_path = doc.file.path
    if not os.path.exists(file_path):
        raise Http404("Файл не найден на сервере.")

    content_type, _ = mimetypes.guess_type(file_path)
    response = FileResponse(
        open(file_path, "rb"),
        content_type=content_type or "application/octet-stream",
        as_attachment=True,
        filename=os.path.basename(file_path),
    )
    return response
