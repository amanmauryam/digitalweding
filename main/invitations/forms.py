from __future__ import annotations

import re

from django import forms
from django.core.exceptions import ValidationError

from . import bihari
from .i18n import LocalizedFormMixin
from .models import (
    CustomerEvent,
    EventFunction,
    GuestBlessing,
    LeadCapture,
    RSVPResponse,
    TemplateTheme,
)

PHONE_RE = re.compile(r"^[6-9]\d{9}$")

DW_INPUT = "dw-input"
DW_SELECT = "dw-select"
DW_TEXTAREA = "dw-textarea"
DW_CHECKBOX = "dw-checkbox"


def phone_validator(value: str) -> str:
    digits = re.sub(r"\D", "", value or "")
    if digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]
    if not PHONE_RE.match(digits):
        raise ValidationError("कृपया 10 अंकों का सही मोबाइल नंबर भरें।")
    return digits


class StyledForm(LocalizedFormMixin, forms.ModelForm):
    """Small helper that applies the DigitalWedding input styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            widget = field.widget
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", DW_CHECKBOX)
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", DW_SELECT)
            elif isinstance(widget, forms.Textarea):
                widget.attrs.setdefault("class", DW_TEXTAREA)
            else:
                widget.attrs.setdefault("class", DW_INPUT)
            if field.required:
                widget.attrs.setdefault("required", "required")


class EventForm(StyledForm):
    class Meta:
        model = CustomerEvent
        fields = [
            "bride_name",
            "groom_name",
            "event_title",
            "family_head_name",
            "native_place",
            "host_phone",
            "primary_language",
            "wedding_date",
            "template",
            "custom_shloka",
            "welcome_message",
        ]
        widgets = {
            "custom_shloka": forms.Textarea(attrs={"rows": 3}),
            "welcome_message": forms.Textarea(attrs={"rows": 3}),
            "wedding_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_host_phone(self):
        return phone_validator(self.cleaned_data["host_phone"])

    def clean_template(self):
        template = self.cleaned_data.get("template")
        if template is not None and not template.is_active:
            raise ValidationError("यह थीम अभी उपलब्ध नहीं है।")
        return template


class EventFunctionForm(StyledForm):
    class Meta:
        model = EventFunction
        fields = [
            "function_code",
            "function_name",
            "date_and_time",
            "venue_name",
            "address",
            "google_maps_url",
        ]
        widgets = {"date_and_time": forms.DateTimeInput(attrs={"type": "datetime-local"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["function_name"].required = False
        self.fields["google_maps_url"].required = False

    def clean(self):
        cleaned = super().clean()
        code = cleaned.get("function_code")
        if code and not cleaned.get("function_name"):
            cleaned["function_name"] = bihari.get_function(code)["bihari_name"]
        return cleaned


class RSVPForm(StyledForm):
    class Meta:
        model = RSVPResponse
        fields = [
            "guest_name",
            "guest_phone",
            "guest_family_tag",
            "attending_status",
            "guest_count",
            "blessing_message",
        ]
        widgets = {
            "guest_name": forms.TextInput(attrs={"placeholder": "आपका नाम"}),
            "guest_phone": forms.TextInput(attrs={"placeholder": "98765 43210"}),
            "guest_family_tag": forms.TextInput(attrs={"placeholder": "शर्मा परिवार"}),
            "blessing_message": forms.Textarea(
                attrs={"rows": 3, "placeholder": "वर-वधू के लिए शुभकामनाएँ"}
            ),
        }
        labels = {
            "attending_status": "आगमन",
            "guest_count": "कुल संख्या",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["guest_family_tag"].required = False
        self.fields["blessing_message"].required = False
        self.fields["attending_status"].required = True

    def clean_guest_phone(self):
        return phone_validator(self.cleaned_data["guest_phone"])

    def clean_guest_count(self):
        count = self.cleaned_data.get("guest_count") or 1
        if count < 1 or count > 20:
            raise ValidationError("1 से 20 के बीच संख्या भरें।")
        return count


class BlessingForm(LocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = GuestBlessing
        fields = ["guest_name", "kind", "message"]
        widgets = {
            "guest_name": forms.TextInput(attrs={"placeholder": "आपका नाम"}),
            "message": forms.TextInput(attrs={"placeholder": "शुभकामनाएँ"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["guest_name"].required = False
        self.fields["message"].required = False


class LeadForm(LocalizedFormMixin, forms.ModelForm):
    class Meta:
        model = LeadCapture
        fields = ["name", "phone_number", "district", "event_date"]
        widgets = {"event_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].required = False
        self.fields["district"].required = False
        self.fields["event_date"].required = False

    def clean_phone_number(self):
        return phone_validator(self.cleaned_data["phone_number"])
