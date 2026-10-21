from django.contrib.auth import views as auth_views
from django.urls import path

from invitations import i18n

from .forms import LoginForm
from .views import signup

app_name = "accounts"


class LocalizedLoginView(auth_views.LoginView):
    """Login view that renders the form in the dialect chosen by the visitor."""

    authentication_form = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["lang"] = i18n.get_language(self.request)
        return kwargs


urlpatterns = [
    path(
        "login/",
        LocalizedLoginView.as_view(),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("signup/", signup, name="signup"),
]
