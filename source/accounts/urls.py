from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup

urlpatterns = [
    path("signup/", signup, name="signup"),

    # если логин у тебя свой, оставь как было, иначе можно удалить
    path("login/", auth_views.LoginView.as_view(
        template_name="registration/login.html"
    ), name="login"),

    # ВОТ ОНО: logout
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
