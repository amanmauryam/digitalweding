from django.contrib.auth import login
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from invitations import i18n

from .forms import SignUpForm


@require_http_methods(["GET", "POST"])
def signup(request):
    form = SignUpForm(request.POST or None, lang=i18n.get_language(request))
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("invitations:dashboard")
    return render(request, "accounts/signup.html", {"form": form})
