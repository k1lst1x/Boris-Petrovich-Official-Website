from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect

from .models import ContactRequest  # <-- ВОТ ЭТОГО НЕ ХВАТАЕТ

@require_POST
@csrf_protect
def send_contact(request):
    ContactRequest.objects.create(
        full_name=(request.POST.get("full_name") or "").strip(),
        email=(request.POST.get("email") or "").strip(),
        phone=(request.POST.get("phone") or "").strip(),
        message=(request.POST.get("message") or "").strip(),
    )

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": True, "message": "Заявка отправлена. Мы свяжемся с вами."})

    return redirect("/")
