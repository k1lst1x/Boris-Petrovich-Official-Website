from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("", views.document_list, name="list"),
    path("category/<slug:category_slug>/", views.document_list_by_category, name="category"),
    path("<slug:slug>/", views.document_detail, name="detail"),
    path("<slug:slug>/download/", views.document_download, name="download"),
    path("<slug:slug>/pay/", views.document_pay_stub, name="pay"),  # заглушка оплаты
]
