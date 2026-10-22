"""Forms for the wedding-website builder."""

from __future__ import annotations

import io
import re

from django import forms
from django.conf import settings

from invitations.i18n import SITE_FORM_LABELS, LocalizedFormMixin

from . import themes
from .models import WeddingEvent, WeddingPhoto, WeddingRSVP, WeddingWebsite

PHONE_RE = re.compile(r"^[6-9]\d{9}$")


class InvitationUploadForm(forms.Form):
    """Accepts a photo or a (possibly scanned) PDF of an invitation card."""

    invitation = forms.FileField(
        label="Invitation card",
        help_text=(
            "Upload a photo, scan or PDF of your invitation card "
            "(JPG, PNG, WEBP or PDF)."
        ),
    )
    acknowledgement = forms.BooleanField(
        required=False,
        label="I own this invitation and allow it to be processed",
    )

    def clean_invitation(self):
        upload = self.cleaned_data["invitation"]
        name = (upload.name or "").lower()
        extension = name.rsplit(".", 1)[-1] if "." in name else ""
        allowed = settings.WEDDING_INVITATION_ALLOWED_EXTENSIONS
        if extension not in allowed:
            raise forms.ValidationError(
                "Unsupported file type. Allowed formats: "
                + ", ".join(ext.upper() for ext in allowed)
                + "."
            )

        max_bytes = settings.WEDDING_INVITATION_MAX_MB * 1024 * 1024
        size = getattr(upload, "size", 0)
        if size > max_bytes:
            raise forms.ValidationError(
                f"The file is larger than {settings.WEDDING_INVITATION_MAX_MB} MB. "
                "Please upload a smaller version."
            )
        if size == 0:
            raise forms.ValidationError("The uploaded file is empty.")

        content = upload.read()
        upload.seek(0)
        if extension == "pdf":
            self._validate_pdf(content, upload)
        else:
            self._validate_image(content, upload)
        return upload

    def _validate_pdf(self, content: bytes, upload) -> None:
        try:
            from pypdf import PdfReader
            from pypdf.errors import PdfReadError
        except ImportError:  # pragma: no cover
            return
        try:
            reader = PdfReader(io.BytesIO(content))
            pages = len(reader.pages)
        except PdfReadError as exc:
            raise forms.ValidationError(
                "The PDF could not be read — it may be damaged or password protected."
            ) from exc
        limit = settings.WEDDING_INVITATION_MAX_PAGES
        if pages > limit:
            raise forms.ValidationError(
                f"The PDF has {pages} pages. Please upload up to {limit} pages."
            )
        upload.page_count = pages

    def _validate_image(self, content: bytes, upload) -> None:
        try:
            from PIL import Image
        except ImportError:  # pragma: no cover
            return
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
        except Exception as exc:
            raise forms.ValidationError(
                "The image could not be read. Please upload a valid JPG, PNG or WEBP file."
            ) from exc


class WeddingDetailsForm(LocalizedFormMixin, forms.ModelForm):
    """Couple, wedding, venue and family details of the wedding website."""

    label_table = SITE_FORM_LABELS

    class Meta:
        model = WeddingWebsite
        fields = [
            "bride_name",
            "groom_name",
            "bride_display_name",
            "groom_display_name",
            "wedding_date",
            "ceremony_time",
            "timezone",
            "language",
            "introduction",
            "welcome_message",
            "story",
            "family_greetings",
            "venue_name",
            "venue_address",
            "venue_city",
            "venue_state",
            "venue_maps_url",
            "contact_name",
            "contact_phone",
            "contact_email",
            "show_contact",
        ]
        widgets = {
            "wedding_date": forms.DateInput(attrs={"type": "date"}),
            "ceremony_time": forms.TimeInput(attrs={"type": "time"}),
            "introduction": forms.Textarea(attrs={"rows": 3}),
            "welcome_message": forms.Textarea(attrs={"rows": 3}),
            "story": forms.Textarea(attrs={"rows": 5}),
            "family_greetings": forms.Textarea(attrs={"rows": 3}),
            "venue_address": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_venue_maps_url(self):
        value = (self.cleaned_data.get("venue_maps_url") or "").strip()
        if value and not value.startswith(("http://", "https://")):
            value = f"https://{value}"
        return value

    def clean_ceremony_time(self):
        """Keep the owner's local wedding time exactly as typed."""

        value = self.cleaned_data.get("ceremony_time")
        return value


class WeddingEventForm(LocalizedFormMixin, forms.ModelForm):
    """One ritual in the wedding schedule."""

    label_table = SITE_FORM_LABELS

    class Meta:
        model = WeddingEvent
        fields = [
            "name",
            "date",
            "start_time",
            "end_time",
            "venue",
            "address",
            "maps_url",
            "dress_code",
            "description",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "address": forms.Textarea(attrs={"rows": 2}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }

    def clean_maps_url(self):
        value = (self.cleaned_data.get("maps_url") or "").strip()
        if value and not value.startswith(("http://", "https://")):
            value = f"https://{value}"
        return value

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_time")
        end = cleaned.get("end_time")
        if start and end and end < start:
            self.add_error("end_time", "The end time cannot be before the start time.")
        return cleaned


class WeddingPhotoForm(LocalizedFormMixin, forms.ModelForm):
    """A photograph for the gallery / couple / family section."""

    label_table = SITE_FORM_LABELS

    class Meta:
        model = WeddingPhoto
        fields = ["image", "caption", "kind"]

    def clean_image(self):
        image = self.cleaned_data["image"]
        max_bytes = settings.WEDDING_PHOTO_MAX_MB * 1024 * 1024
        if getattr(image, "size", 0) > max_bytes:
            raise forms.ValidationError(
                f"The photo is larger than {settings.WEDDING_PHOTO_MAX_MB} MB."
            )
        try:
            from PIL import Image

            with Image.open(image) as img:
                img.verify()
        except Exception as exc:
            raise forms.ValidationError(
                "The photo could not be read. Please upload a valid image file."
            ) from exc
        return image


class ThemeForm(forms.Form):
    """Theme picker — only themes that exist in the catalogue."""

    theme = forms.ChoiceField(
        choices=themes.theme_choices(),
        widget=forms.RadioSelect,
        label="Website theme",
    )


class CustomizeForm(LocalizedFormMixin, forms.ModelForm):
    """Optional customisation: colours, sections, contact details."""

    label_table = SITE_FORM_LABELS

    class Meta:
        model = WeddingWebsite
        fields = [
            "accent_color",
            "show_countdown",
            "show_story",
            "show_gallery",
            "show_family",
            "show_rsvp",
            "rsvp_ask_guest_count",
            "rsvp_ask_message",
            "contact_name",
            "contact_phone",
            "contact_email",
            "show_contact",
        ]
        widgets = {
            "show_countdown": forms.CheckboxInput(),
            "show_story": forms.CheckboxInput(),
            "show_gallery": forms.CheckboxInput(),
            "show_family": forms.CheckboxInput(),
            "show_rsvp": forms.CheckboxInput(),
            "rsvp_ask_guest_count": forms.CheckboxInput(),
            "rsvp_ask_message": forms.CheckboxInput(),
            "show_contact": forms.CheckboxInput(),
        }


class PublicRSVPForm(LocalizedFormMixin, forms.ModelForm):
    """The guest facing RSVP form (no personal data beyond a phone number)."""

    label_table = SITE_FORM_LABELS

    website = forms.CharField(required=False, widget=forms.HiddenInput)
    company = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
    started_at = forms.CharField(required=False, widget=forms.HiddenInput)

    class Meta:
        model = WeddingRSVP
        fields = ["guest_name", "guest_phone", "attending", "guest_count", "message"]
        widgets = {
            "guest_name": forms.TextInput(
                attrs={"class": "w-input", "autocomplete": "name"}
            ),
            "guest_phone": forms.TextInput(
                attrs={
                    "class": "w-input",
                    "inputmode": "numeric",
                    "autocomplete": "tel",
                    "placeholder": "9876543210",
                }
            ),
            "guest_count": forms.NumberInput(
                attrs={"class": "w-input", "min": 1, "max": 20}
            ),
            "message": forms.Textarea(attrs={"class": "w-input", "rows": 3}),
        }

    def clean_guest_phone(self):
        phone = re.sub(r"\D", "", self.cleaned_data.get("guest_phone") or "")
        if phone.startswith("91") and len(phone) == 12:
            phone = phone[2:]
        if not PHONE_RE.match(phone):
            raise forms.ValidationError("Please enter a valid 10 digit mobile number.")
        return phone

    def clean_guest_count(self):
        count = self.cleaned_data.get("guest_count") or 1
        if count < 1 or count > 20:
            raise forms.ValidationError("Please enter a number between 1 and 20.")
        return count

    def clean_company(self):
        """Honeypot: real guests never fill this hidden field."""

        if self.cleaned_data.get("company"):
            raise forms.ValidationError("Your response could not be submitted.")
        return ""

    def clean_started_at(self):
        """Time trap: the form must stay open for a few seconds."""

        raw = self.cleaned_data.get("started_at") or ""
        try:
            started = float(raw)
        except (TypeError, ValueError):
            return raw
        import time as _time

        if _time.time() - started < settings.WEDDING_RSVP_MIN_SECONDS:
            raise forms.ValidationError("Please wait a moment before submitting.")
        return raw
