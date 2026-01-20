from django.shortcuts import render

from news.models import NewsPost
from documents.models import Document


def home(request):
    news_posts = (
        NewsPost.objects
        .filter(is_published=True)
        .order_by("-published_at", "-created_at")[:3]
    )

    documents = (
        Document.objects
        .filter(is_published=True, is_open=True)
        .select_related("category")
        .order_by("-created_at")[:3]
    )

    return render(request, "core/home.html", {
        "news_posts": news_posts,
        "documents": documents,
    })
