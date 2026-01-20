from django.urls import path
from . import views

app_name = "news"

urlpatterns = [
    path("", views.news_list, name="list"),
    path("category/<slug:category_slug>/", views.news_by_category, name="category"),
    path("<slug:slug>/", views.news_detail, name="detail"),
]
