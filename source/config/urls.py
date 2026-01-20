from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # apps
    path("", include(("core.urls", "core"), namespace="core")),  # главная
    path("news/", include(("news.urls", "news"), namespace="news")),
    path("documents/", include(("documents.urls", "documents"), namespace="documents")),
    path("portfolio/", include(("portfolio.urls", "portfolio"), namespace="portfolio")),
    path("contacts/", include(("contacts.urls", "contacts"), namespace="contacts")),

    # auth (reset/смена пароля и т.д.)
    path("accounts/", include("django.contrib.auth.urls")),

    # короткие урлы
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # регистрация (signup)
    path("", include("accounts.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
