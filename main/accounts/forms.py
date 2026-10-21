from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from invitations.i18n import LocalizedFormMixin

from .models import User


class SignUpForm(LocalizedFormMixin, UserCreationForm):
    """Account creation form with dialect-aware labels and placeholders."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email", "phone_number", "home_district")
        widgets = {
            "phone_number": forms.TextInput(attrs={"placeholder": "+91 98765 43210"}),
            "home_district": forms.TextInput(attrs={"placeholder": "Patna"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "dw-input")
        self.fields["home_district"].required = False


class LoginForm(LocalizedFormMixin, AuthenticationForm):
    """Sign-in form whose field names follow the selected dialect."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.setdefault("class", "dw-input")
