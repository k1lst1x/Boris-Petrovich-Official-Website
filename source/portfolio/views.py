from django.shortcuts import get_object_or_404, render

from .models import PortfolioPage, Case
from documents.models import Document, DocumentCategory


def portfolio_index(request):
    pages = PortfolioPage.objects.filter(is_published=True).order_by("order", "title")
    return render(request, "portfolio/portfolio_index.html", {"pages": pages})


def portfolio_page_detail(request, page_slug: str):
    page = get_object_or_404(PortfolioPage, slug=page_slug, is_published=True)

    cases = (
        page.cases.filter(is_published=True)
        .select_related()  # безопасно, даже если не нужно
        .order_by("-created_at")
    )

    # Документы для страницы направления (логика: категория документов совпадает со slug страницы)
    documents = Document.objects.none()
    category = DocumentCategory.objects.filter(slug=page.slug, is_active=True).first()
    if category:
        documents = (
            Document.objects.filter(category=category, is_published=True)
            .order_by("-created_at")
        )

    user = request.user
    for d in documents:
        d.user_can_access = d.can_user_access(user)
        d.user_needs_login = (d.is_paid and not user.is_authenticated)

    return render(
        request,
        "portfolio/portfolio.html",
        {
            "page": page,
            "cases": cases,
            "documents": documents,
        },
    )


def case_detail(request, slug: str):
    case = get_object_or_404(Case, slug=slug, is_published=True)

    images = case.images.filter(is_active=True).order_by("order", "id")
    attachments = case.attachments.filter(is_active=True).order_by("order", "id")

    # Документы привязанные к кейсу через промежуточную модель CaseDocument (у тебя должно быть related_name="case_documents")
    case_docs = (
        case.case_documents.filter(is_active=True)
        .select_related("document", "document__category")
        .order_by("order", "id")
    )

    user = request.user
    for cd in case_docs:
        d = cd.document
        d.user_can_access = d.can_user_access(user)
        d.user_needs_login = (d.is_paid and not user.is_authenticated)

    return render(
        request,
        "portfolio/portfolio.html",
        {
            "case": case,
            "images": images,
            "attachments": attachments,
            "case_docs": case_docs,
        },
    )
