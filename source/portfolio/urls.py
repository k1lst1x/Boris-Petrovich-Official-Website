from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    path("", views.portfolio_index, name="index"),                    # /portfolio/
    path("case/<slug:slug>/", views.case_detail, name="case_detail"), # /portfolio/case/<slug>/
    path("<slug:page_slug>/", views.portfolio_page_detail, name="page"),  # /portfolio/<page_slug>/
]
