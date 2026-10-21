from __future__ import annotations

import secrets

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from . import bihari
from .transliterate import transliterate

DEFAULT_SHLOKA = "वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ। निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा॥"
DEFAULT_WELCOME = (
    "परम पिता परमेश्वर की असीम अनुकंपा से हमारे सुपुत्र/सुपुत्री के शुभ विवाह अवसर पर "
    "आपका हार्दिक अभिनंदन है।"
)


class InvitationCategory(models.Model):
    """e.g. Biyah (Wedding), Chhath Puja, Griha Pravesh, Mundan."""

    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = "Invitation categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class TemplateTheme(models.Model):
    """A ready-made invitation skin (Mithila, Royal Rajputana, …)."""

    THEME_STYLES = bihari.THEME_STYLES

    category = models.ForeignKey(InvitationCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    template_code = models.CharField(max_length=100)  # e.g. 'kohbar_rajputana'
    style_type = models.CharField(
        max_length=20, choices=THEME_STYLES, default="MITHILA"
    )
    preview_image = models.ImageField(upload_to="templates/previews/", blank=True)
    default_audio_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category__name", "title"]

    def __str__(self):
        return f"{self.title} ({self.get_style_type_display()})"

    @property
    def preset(self) -> dict:
        return bihari.THEME_STYLE_PRESETS.get(self.style_type, {})

    @property
    def accent_color(self) -> str:
        return self.preset.get("primary", bihari.PALETTE["sindoor"])


class CustomerEvent(models.Model):
    """A single wedding / sanskar invitation owned by a customer."""

    LANG_CHOICES = [
        ("HI", "Hindi"),
        ("MAI", "Maithili"),
        ("BHO", "Bhojpuri"),
        ("EN", "English"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    template = models.ForeignKey(
        TemplateTheme, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Event Info
    bride_name = models.CharField(max_length=100)
    groom_name = models.CharField(max_length=100)
    event_title = models.CharField(max_length=200, help_text="e.g., Aman weds Priya")
    slug = models.SlugField(unique=True)

    # Bihari Host Context
    family_head_name = models.CharField(
        max_length=150, help_text="e.g., Shri Ramakant Roy"
    )
    native_place = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="e.g., Gram: Nehra, Jila: Darbhanga",
    )
    host_phone = models.CharField(max_length=15)

    primary_language = models.CharField(
        max_length=5, choices=LANG_CHOICES, default="HI"
    )
    wedding_date = models.DateField()
    custom_shloka = models.TextField(default=DEFAULT_SHLOKA)
    welcome_message = models.TextField(default=DEFAULT_WELCOME)

    # Analytics
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-wedding_date", "-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            raw = f"{self.groom_name}-weds-{self.bride_name}-{(self.host_phone or '')[-4:]}"
            base = slugify(transliterate(raw)) or "invitation"
            slug = base
            while CustomerEvent.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{secrets.token_hex(2)}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.event_title

    def get_absolute_url(self) -> str:
        return reverse("invitations:event_detail", kwargs={"slug": self.slug})

    @property
    def is_multilingual(self) -> bool:
        return True

    @property
    def total_rsvps(self) -> int:
        return self.rsvps.count()

    @property
    def attending_count(self) -> int:
        return sum(r.guest_count for r in self.rsvps.filter(attending_status="YES"))

    @property
    def blessing_count(self) -> int:
        return self.blessings.count()

    @property
    def accent_color(self) -> str:
        if self.template_id and self.template:
            return self.template.accent_color
        return bihari.PALETTE["sindoor"]

    @property
    def theme_style(self) -> str:
        if self.template_id and self.template:
            return self.template.style_type
        return "MITHILA"

    def functions_in_order(self):
        return self.functions.select_related().order_by("date_and_time")

    def increment_views(self, count: int = 1) -> None:
        CustomerEvent.objects.filter(pk=self.pk).update(
            view_count=models.F("view_count") + count
        )


class EventFunction(models.Model):
    """One ritual in the wedding calendar — Tilak, Matkor, Haldi, …"""

    event = models.ForeignKey(
        CustomerEvent, related_name="functions", on_delete=models.CASCADE
    )
    function_code = models.CharField(
        max_length=20,
        choices=bihari.function_options(),
        default="TILAK",
        help_text="Bihari ritual identifier",
    )
    function_name = models.CharField(
        max_length=100, help_text="Tilak, Matkor, Haldi, Dwar Puja, Jaimala, Preeti Bhoj"
    )
    date_and_time = models.DateTimeField()
    venue_name = models.CharField(
        max_length=200, help_text="e.g., Maurya Hotel, Patna / Village Residence"
    )
    address = models.TextField()
    google_maps_url = models.URLField(blank=True, null=True)

    class Meta:
        ordering = ["date_and_time"]

    def __str__(self):
        return f"{self.function_name} - {self.event.event_title}"

    @property
    def meta(self) -> dict:
        return bihari.get_function(self.function_code)

    @property
    def accent_color(self) -> str:
        return self.meta["accent"]

    @property
    def folk_music(self) -> str:
        return self.meta["folk_music"]

    @property
    def devanagari_name(self) -> str:
        return self.meta["devanagari"]


class RSVPResponse(models.Model):
    """Guest confirmation — 'Aayenge' or 'Sneh Sahit Kshama'."""

    ATTENDING_CHOICES = [
        ("YES", "Aayenge (Aastha/Aadhar)"),
        ("NO", "Sneh Sahit Kshama"),
    ]

    event = models.ForeignKey(
        CustomerEvent, related_name="rsvps", on_delete=models.CASCADE
    )
    guest_name = models.CharField(max_length=150)
    guest_phone = models.CharField(max_length=15)
    guest_family_tag = models.CharField(
        max_length=150,
        blank=True,
        null=True,
        help_text="e.g., Verma Parivar",
    )
    attending_status = models.CharField(max_length=20, choices=ATTENDING_CHOICES)
    guest_count = models.PositiveIntegerField(default=1)
    blessing_message = models.TextField(
        blank=True, null=True, help_text="Subhkaamnaayein for Bride & Groom"
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]

    def __str__(self):
        return f"{self.guest_name} - {self.get_attending_status_display()}"

    @property
    def is_attending(self) -> bool:
        return self.attending_status == "YES"


class GuestBlessing(models.Model):
    """The virtual Paan / Laddoo greeting badge sent from the guest side."""

    KIND_CHOICES = [
        ("PAAN", "Paan"),
        ("LADDOO", "Laddoo"),
        ("GOLI", "Goli / Chokha"),
    ]

    event = models.ForeignKey(
        CustomerEvent, related_name="blessings", on_delete=models.CASCADE
    )
    guest_name = models.CharField(max_length=150, blank=True)
    kind = models.CharField(max_length=10, choices=KIND_CHOICES, default="PAAN")
    message = models.CharField(max_length=250, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.guest_name or 'Guest'} - {self.get_kind_display()}"


class LeadCapture(models.Model):
    """Free-tier lead: 'Send me my customised invitation'."""

    phone_number = models.CharField(max_length=15)
    name = models.CharField(max_length=150, blank=True)
    district = models.CharField(max_length=100, blank=True)
    event_date = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=50, default="landing")
    created_at = models.DateTimeField(auto_now_add=True)
    is_contacted = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Lead"
        verbose_name_plural = "Leads"

    def __str__(self):
        return f"{self.name or 'Lead'} - {self.phone_number}"
