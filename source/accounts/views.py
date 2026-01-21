from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        # классы нужны и при POST, чтобы при ошибках форма выглядела нормально
        for name in ("username", "password1", "password2"):
            form.fields[name].widget.attrs.update({"class": "auth-input"})

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect(request.POST.get("next") or "/")
    else:
        form = UserCreationForm()
        for name in ("username", "password1", "password2"):
            form.fields[name].widget.attrs.update({"class": "auth-input"})

    return render(request, "registration/signup.html", {"form": form, "next": request.GET.get("next")})
