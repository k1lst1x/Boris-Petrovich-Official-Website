from django.shortcuts import get_object_or_404, render
from .models import NewsPost, NewsCategory


def news_list(request):
    posts = (
        NewsPost.objects
        .filter(is_published=True)
        .select_related("category")
        .order_by("-published_at", "-created_at")
    )
    categories = NewsCategory.objects.filter(is_active=True).order_by("order", "title")

    return render(request, "news/news_list.html", {
        "posts": posts,
        "categories": categories,
    })


def news_by_category(request, category_slug: str):
    category = get_object_or_404(NewsCategory, slug=category_slug, is_active=True)

    posts = (
        category.posts
        .filter(is_published=True)
        .select_related("category")
        .order_by("-published_at", "-created_at")
    )

    categories = NewsCategory.objects.filter(is_active=True).order_by("order", "title")

    return render(request, "news/news_list.html", {
        "posts": posts,
        "categories": categories,
        "current_category": category,
    })


def news_detail(request, slug: str):
    post = get_object_or_404(
        NewsPost.objects.select_related("category"),
        slug=slug,
        is_published=True,
    )
    return render(request, "news/news_detail.html", {"post": post})
