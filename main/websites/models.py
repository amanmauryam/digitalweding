"""Models for the *wedding website* product.

Flow: a customer uploads an existing invitation card → the text is extracted
(``websites.extraction``) → the suggestions are stored on a draft
:class:`WeddingWebsite` → the owner reviews and corrects them → the owner
picks a theme, adds photos and events → the owner explicitly publishes it.

Everything that is not explicitly published stays private: drafts are only
reachable through the owner's dashboard and the original invitation file is
kept in a private storage area.
"""

from __future__ import annotations

import secrets
from datetime import date

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from invitations.transliterate import transliterate

from . import themes
from .storage import private_storage, private_upload_to


class WeddingWebsite(models.Model):
    """One published (or draft) wedding microsite."""

    STATUS_DRAFT = "draft"
    STATUS_PUBLISHED = "published"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_PUBLISHED, "Published"),
        (STATUS_ARCHIVED, "Archived"),
    ]

    LANGUAGE_CHOICES = [
        ("hi", "हिन्दी"),
        ("mai", "मैथिली"),
        ("bho", "भोजपुरी"),
        ("en", "English"),
    ]

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wedding_websites",
    )

    # --- Couple -----------------------------------------------------------
    bride_name = models.CharField(max_length=120, blank=True)
    groom_name = models.CharField(max_length=120, blank=True)
    bride_display_name = models.CharField(
        max_length=120, blank=True, help_text="Optional Latin spelling, e.g. Priya"
    )
    groom_display_name = models.CharField(
        max_length=120, blank=True, help_text="Optional Latin spelling, e.g. Aman"
    )
    title = models.CharField(max_length=200, blank=True)

    # --- Wedding ----------------------------------------------------------
    wedding_date = models.DateField(null=True, blank=True)
    ceremony_time = models.TimeField(
        null=True, blank=True, help_text="Local wedding time (no time-zone shifting)"
    )
    timezone = models.CharField(max_length=64, default="Asia/Kolkata")
    language = models.CharField(
        max_length=5, choices=LANGUAGE_CHOICES, default="hi"
    )
    introduction = models.TextField(
        blank=True, help_text="Short introduction shown under the couple's names"
    )
    story = models.TextField(blank=True, help_text="How the couple met")
    welcome_message = models.TextField(blank=True)
    family_greetings = models.TextField(blank=True)

    # --- Venue ------------------------------------------------------------
    venue_name = models.CharField(max_length=200, blank=True)
    venue_address = models.TextField(blank=True)
    venue_city = models.CharField(max_length=100, blank=True)
    venue_state = models.CharField(max_length=100, blank=True)
    venue_maps_url = models.URLField(blank=True)

    # --- Contact (never public unless show_contact is on) ------------------
    contact_name = models.CharField(max_length=150, blank=True)
    contact_phone = models.CharField(max_length=32, blank=True)
    contact_email = models.EmailField(blank=True)
    show_contact = models.BooleanField(default=False)

    # --- Look & feel ------------------------------------------------------
    theme = models.CharField(
        max_length=40, choices=themes.theme_choices(), default=themes.DEFAULT_THEME
    )
    accent_color = models.CharField(max_length=20, blank=True)

    show_countdown = models.BooleanField(default=True)
    show_story = models.BooleanField(default=True)
    show_gallery = models.BooleanField(default=True)
    show_family = models.BooleanField(default=True)
    show_rsvp = models.BooleanField(default=True)
    rsvp_ask_guest_count = models.BooleanField(default=True)
    rsvp_ask_message = models.BooleanField(default=True)

    # --- Source invitation (private) --------------------------------------
    source_invitation = models.FileField(
        upload_to=private_upload_to,
        storage=private_storage,
        blank=True,
        null=True,
        help_text="Original invitation card — kept private, never publicly served",
    )
    source_filename = models.CharField(max_length=255, blank=True)
    source_text = models.TextField(blank=True, help_text="Extracted text (private)")
    extracted_data = models.JSONField(
        default=dict, blank=True, help_text="Field -> {value, confidence, source}"
    )
    extraction_engine = models.CharField(max_length=60, blank=True)
    extraction_warnings = models.TextField(blank=True)

    # --- Publication ------------------------------------------------------
    slug = models.SlugField(max_length=180, unique=True)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_DRAFT
    )
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status", "-created_at"]),
            models.Index(fields=["owner", "-created_at"]),
        ]

    def __str__(self):
        return self.display_title or f"Wedding website #{self.pk}"

    # -- helpers ----------------------------------------------------------
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.build_slug()
        if not self.title:
            self.title = self.default_title()
        super().save(*args, **kwargs)

    def build_slug(self) -> str:
        """Stable, human readable and collision safe public URL segment."""

        raw = f"{self.groom_name}-weds-{self.bride_name}"
        base = slugify(transliterate(raw))[:140] or "wedding"
        if not base.startswith("wedding"):
            base = base
        slug = base
        while (
            WeddingWebsite.objects.filter(slug=slug).exclude(pk=self.pk).exists()
        ):
            slug = f"{base}-{secrets.token_hex(2)}"
        return slug

    def default_title(self) -> str:
        if self.groom_name and self.bride_name:
            return f"{self.groom_name} व {self.bride_name}"
        if self.groom_name:
            return self.groom_name
        if self.bride_name:
            return self.bride_name
        return ""

    @property
    def display_title(self) -> str:
        return self.title or self.default_title()

    @property
    def theme_config(self) -> themes.Theme:
        return themes.get_theme(self.theme)

    @property
    def is_published(self) -> bool:
        return self.status == self.STATUS_PUBLISHED

    @property
    def display_bride(self) -> str:
        return self.bride_display_name or self.bride_name

    @property
    def display_groom(self) -> str:
        return self.groom_display_name or self.groom_name

    @property
    def couple_line(self) -> str:
        if self.display_groom and self.display_bride:
            return f"{self.display_groom} & {self.display_bride}"
        return self.display_groom or self.display_bride

    @property
    def accent(self) -> str:
        theme = self.theme_config
        if self.accent_color and theme.allows_accent(self.accent_color):
            return self.accent_color
        return theme.colors["accent"]

    @property
    def extracted_fields(self) -> dict:
        return self.extracted_data if isinstance(self.extracted_data, dict) else {}

    @property
    def unconfirmed_fields(self) -> list[str]:
        return [
            key
            for key, payload in self.extracted_fields.items()
            if isinstance(payload, dict) and not payload.get("confirmed")
        ]

    @property
    def needs_review(self) -> bool:
        return bool(self.unconfirmed_fields)

    @property
    def rsvp_count(self) -> int:
        return self.rsvps.count()

    @property
    def attending_count(self) -> int:
        return sum(r.guest_count for r in self.rsvps.filter(attending=True))

    @property
    def has_events(self) -> bool:
        return self.events.exists()

    def get_absolute_url(self) -> str:
        return reverse("websites:public_site", kwargs={"slug": self.slug})

    def public_url(self) -> str:
        base = settings.DEFAULT_SITE_URL.rstrip("/")
        return f"{base}{self.get_absolute_url()}"

    def increment_views(self, count: int = 1) -> None:
        WeddingWebsite.objects.filter(pk=self.pk).update(
            view_count=models.F("view_count") + count
        )

    def publish(self) -> None:
        self.status = self.STATUS_PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=["status", "published_at", "updated_at"])

    def unpublish(self) -> None:
        self.status = self.STATUS_DRAFT
        self.published_at = None
        self.save(update_fields=["status", "published_at", "updated_at"])


class WeddingEvent(models.Model):
    """One entry of the wedding schedule (Haldi, Mehndi, Sangeet, Vivah…)."""

    website = models.ForeignKey(
        WeddingWebsite, on_delete=models.CASCADE, related_name="events"
    )
    name = models.CharField(max_length=120)
    date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    venue = models.CharField(max_length=200, blank=True)
    address = models.TextField(blank=True)
    maps_url = models.URLField(blank=True)
    dress_code = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date", "start_time", "order", "id"]
        indexes = [models.Index(fields=["website", "date"])]

    def __str__(self):
        return f"{self.name} — {self.website.display_title}"

    @property
    def date_or_empty(self) -> date | None:
        return self.date


class WeddingPhoto(models.Model):
    """Couple / family / gallery photograph used on the public site."""

    KIND_COUPLE = "couple"
    KIND_FAMILY = "family"
    KIND_GALLERY = "gallery"
    KIND_CHOICES = [
        (KIND_COUPLE, "Couple"),
        (KIND_FAMILY, "Family"),
        (KIND_GALLERY, "Gallery"),
    ]

    website = models.ForeignKey(
        WeddingWebsite, on_delete=models.CASCADE, related_name="photos"
    )
    image = models.ImageField(upload_to="wedding-websites/photos/")
    thumbnail = models.ImageField(
        upload_to="wedding-websites/thumbs/", blank=True, null=True
    )
    caption = models.CharField(max_length=200, blank=True)
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default=KIND_GALLERY)
    order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["kind", "order", "-created_at"]

    def __str__(self):
        return self.caption or f"Photo #{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.build_thumbnail()

    def build_thumbnail(self) -> None:
        """Create a small optimised copy used in lists and the editor."""

        try:
            from PIL import Image
        except ImportError:  # pragma: no cover - Pillow is a hard requirement
            return
        try:
            with Image.open(self.image) as img:
                img = img.convert("RGB")
                img.thumbnail((480, 480))
                from django.core.files.base import ContentFile

                buffer = __import__("io").BytesIO()
                img.save(buffer, format="JPEG", quality=82, optimize=True)
                buffer.seek(0)
                name = f"thumb-{self.pk or 'new'}.jpg"
                self.thumbnail.save(name, ContentFile(buffer.read()), save=False)
        except Exception:  # pragma: no cover - a broken image must not 500
            return
        WeddingPhoto.objects.filter(pk=self.pk).update(thumbnail=self.thumbnail.name)

    def delete(self, *args, **kwargs):
        for field in (self.image, self.thumbnail):
            try:
                if field:
                    field.storage.delete(field.name)
            except Exception:  # pragma: no cover
                pass
        super().delete(*args, **kwargs)


class WeddingRSVP(models.Model):
    """A guest response on a published wedding website."""

    website = models.ForeignKey(
        WeddingWebsite, on_delete=models.CASCADE, related_name="rsvps"
    )
    guest_name = models.CharField(max_length=150)
    guest_phone = models.CharField(max_length=20)
    attending = models.BooleanField(default=True)
    guest_count = models.PositiveSmallIntegerField(default=1)
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["website", "guest_phone"], name="unique_rsvp_per_website_phone"
            )
        ]
        indexes = [models.Index(fields=["website", "-created_at"])]

    def __str__(self):
        status = "attending" if self.attending else "regret"
        return f"{self.guest_name} ({status})"
