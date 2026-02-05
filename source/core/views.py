from django.shortcuts import render

from news.models import NewsPost
from documents.models import Document
from .models import Recommendation


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

    recommendations = (
        Recommendation.objects
        .all()
        .order_by("order", "-created_at")[:4]
    )

    return render(request, "core/home.html", {
        "news_posts": news_posts,
        "documents": documents,
        "recommendations": recommendations,
    })


def recommendations_list(request):
    recommendations = Recommendation.objects.all().order_by("order", "-created_at")

    return render(request, "core/recommendations_list.html", {
        "recommendations": recommendations
    })
