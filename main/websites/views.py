"""Views for the wedding-website builder.

Two audiences:

* the **owner** — everything behind ``@login_required`` plus an explicit
  ownership check on every single action.
* the **guest** — the published microsite (``/wedding/<slug>/``) and its RSVP
  form.  Drafts and archived sites answer with a proper 404.
"""

from __future__ import annotations

import time

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.cache import cache
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from invitations import i18n

from . import extraction, services, themes
from .forms import (
    CustomizeForm,
    InvitationUploadForm,
    PublicRSVPForm,
    ThemeForm,
    WeddingDetailsForm,
    WeddingEventForm,
    WeddingPhotoForm,
)
from .models import WeddingEvent, WeddingPhoto, WeddingRSVP, WeddingWebsite

STEP_ORDER = [
    ("create", "Upload"),
    ("review", "Details"),
    ("themes", "Theme"),
    ("events", "Schedule"),
    ("photos", "Photos"),
    ("customize", "Customise"),
    ("preview", "Preview"),
    ("publish", "Publish"),
]

STEP_LABEL_KEYS = {
    "create": "site_step_upload",
    "review": "site_step_details",
    "themes": "site_step_theme",
    "events": "site_step_schedule",
    "photos": "site_step_photos",
    "customize": "site_step_customise",
    "preview": "site_step_preview",
    "publish": "site_step_publish",
}


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
DETAIL_GROUPS = [
    ("site_group_couple", ["bride_name", "groom_name", "bride_display_name", "groom_display_name"]),
    ("site_group_wedding", ["wedding_date", "ceremony_time", "timezone", "language"]),
    ("site_group_story", ["introduction", "welcome_message", "story", "family_greetings"]),
    ("site_group_venue", ["venue_name", "venue_address", "venue_city", "venue_state", "venue_maps_url"]),
    ("site_group_contact", ["contact_name", "contact_phone", "contact_email", "show_contact"]),
]


def _details_groups(form) -> list[dict]:
    """Group the review form into readable sections."""

    groups = []
    for key, names in DETAIL_GROUPS:
        fields = [form[name] for name in names if name in form.fields]
        if fields:
            groups.append({"key": key, "fields": fields})
    return groups


def _owned_website(request, slug: str) -> WeddingWebsite:
    website = get_object_or_404(WeddingWebsite, slug=slug)
    if website.owner_id != request.user.id:
        raise Http404("You do not have access to this wedding website.")
    return website


def _editor_context(request, website: WeddingWebsite, active: str) -> dict:
    lang = i18n.get_language(request)
    steps = []
    for code, _fallback in STEP_ORDER:
        if code == "create":
            url = reverse("websites:create")
        else:
            url = reverse(f"websites:{code}", kwargs={"slug": website.slug})
        steps.append(
            {
                "code": code,
                "label": i18n.get_string(STEP_LABEL_KEYS[code], lang),
                "url": url,
                "active": code == active,
            }
        )
    return {
        "website": website,
        "active_step": active,
        "steps": steps,
        "themes": themes.THEMES,
    }


def _is_rate_limited(key: str, limit: int, window: int) -> bool:
    """Very small cache based throttle for the public RSVP endpoint."""

    try:
        count = cache.get(key, 0)
        if count >= limit:
            return True
        cache.set(key, count + 1, window)
    except Exception:  # pragma: no cover - cache backend hiccup
        return False
    return False


def _site_context(request, website: WeddingWebsite, is_preview: bool = False) -> dict:
    """Context for the microsite.

    The microsite always speaks the language the couple chose, independently
    of the language the visitor happens to browse in.
    """

    lang = i18n.normalise(website.language)
    context = services.public_site_context(website)
    days_left = None
    if website.wedding_date:
        from datetime import date as _date

        days_left = (website.wedding_date - _date.today()).days
    context.update(
        {
            "dw_lang": lang,
            "dw_lang_meta": i18n.LANG_META,
            "dw_active_lang": next(
                (item for item in i18n.LANG_META if item["code"] == lang),
                i18n.LANG_META[0],
            ),
            "is_preview": is_preview,
            "days_left": days_left,
            "couple_photo": website.photos.filter(kind="couple").first(),
            "gallery_photos": website.photos.filter(kind="gallery"),
            "family_photos": website.photos.filter(kind="family"),
            "seo_title": _seo_title(website),
            "seo_description": _seo_description(website),
            "json_ld": _json_ld(website),
        }
    )
    return context


def _seo_title(website: WeddingWebsite) -> str:
    title = website.display_title or "Wedding"
    if website.wedding_date:
        title = f"{title} · {website.wedding_date.strftime('%d %B %Y')}"
    return f"{title} — Wedding invitation"


def _seo_description(website: WeddingWebsite) -> str:
    parts = []
    if website.couple_line:
        parts.append(f"{website.couple_line} की शादी का निमंत्रण")
    if website.wedding_date:
        parts.append(website.wedding_date.strftime("%d %B %Y"))
    if website.venue_name:
        parts.append(website.venue_name)
    if website.venue_city:
        parts.append(website.venue_city)
    if not parts:
        parts.append("Wedding invitation, schedule, venue and RSVP.")
    return " · ".join(parts)[:300]


def _json_ld(website: WeddingWebsite) -> str:
    """Schema.org Event payload for rich search results."""

    import json

    data = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": website.display_title,
        "description": _seo_description(website),
        "startDate": website.wedding_date.isoformat() if website.wedding_date else "",
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled",
        "organizer": {"@type": "Person", "name": website.couple_line},
        "location": {
            "@type": "Place",
            "name": website.venue_name or website.venue_address,
            "address": {
                "@type": "PostalAddress",
                "streetAddress": website.venue_address,
                "addressLocality": website.venue_city,
                "addressRegion": website.venue_state,
                "addressCountry": "IN",
            },
        },
    }
    if website.ceremony_time:
        data["startDate"] = f"{website.wedding_date.isoformat()}T{website.ceremony_time.strftime('%H:%M:%S')}"
    return json.dumps(data, ensure_ascii=False)


def _apply_extraction(website: WeddingWebsite, result: extraction.ExtractionResult) -> None:
    """Copy the extracted suggestions into the draft, flagged as unconfirmed."""

    mapping = {
        "groom_name": "groom_name",
        "bride_name": "bride_name",
        "wedding_date": "wedding_date",
        "ceremony_time": "ceremony_time",
        "venue_name": "venue_name",
        "venue_address": "venue_address",
        "venue_city": "venue_city",
        "venue_state": "venue_state",
        "language": "language",
    }
    for key, field_name in mapping.items():
        value = result.value(key)
        if not value:
            continue
        field = WeddingWebsite._meta.get_field(field_name)
        if field_name in {"wedding_date", "ceremony_time"}:
            parsed = _parse_temporal(field, value)
            if parsed is None:
                continue
            setattr(website, field_name, parsed)
        else:
            setattr(website, field_name, value[: field.max_length or 200])

    website.extracted_data = {
        key: {
            "value": payload.get("value", ""),
            "confidence": payload.get("confidence", 0),
            "source": payload.get("source", ""),
            "confirmed": False,
        }
        for key, payload in result.fields.items()
    }
    website.source_text = result.text
    website.extraction_engine = result.engine
    website.extraction_warnings = " ".join(result.warnings)
    website.save()


def _parse_temporal(field, value: str):
    from datetime import date, time as dtime

    if field.name == "wedding_date":
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    if field.name == "ceremony_time":
        try:
            hour, minute = (int(part) for part in value.split(":")[:2])
            return dtime(hour % 24, minute)
        except (ValueError, TypeError):
            return None
    return value


# ---------------------------------------------------------------------------
# owner: dashboard + creation
# ---------------------------------------------------------------------------
@login_required
def dashboard(request):
    websites = WeddingWebsite.objects.filter(owner=request.user).prefetch_related(
        "rsvps"
    )
    return render(
        request,
        "websites/dashboard.html",
        {
            "websites": websites,
            "published_count": sum(1 for w in websites if w.is_published),
            "draft_count": sum(1 for w in websites if w.status == WeddingWebsite.STATUS_DRAFT),
        },
    )


@login_required
def create(request):
    """Step 1 — upload an invitation card, or start from a blank draft."""

    posted = request.method == "POST"
    form = InvitationUploadForm(
        request.POST if posted else None,
        request.FILES if posted else None,
    )

    if posted and "manual" in request.POST:
        website = WeddingWebsite.objects.create(owner=request.user)
        messages.success(request, "Blank wedding website created — add the details.")
        return redirect("websites:review", slug=website.slug)

    if posted and form.is_valid():
        upload = form.cleaned_data["invitation"]
        website = WeddingWebsite.objects.create(owner=request.user)
        try:
            result = extraction.extract_upload(upload)
        except extraction.OCRUnavailable as exc:
            _store_invitation(website, upload)
            website.extraction_warnings = str(exc)
            website.save()
            messages.warning(request, str(exc))
            return redirect("websites:review", slug=website.slug)
        except extraction.ExtractionError as exc:
            _store_invitation(website, upload)
            website.extraction_warnings = str(exc)
            website.save()
            messages.error(request, str(exc))
            return redirect("websites:review", slug=website.slug)

        _store_invitation(website, upload)
        _apply_extraction(website, result)
        messages.success(
            request,
            "Invitation read — please check the details we found before continuing.",
        )
        return redirect("websites:review", slug=website.slug)

    return render(request, "websites/create.html", {"form": form})


def _store_invitation(website: WeddingWebsite, upload) -> None:
    """Keep the original card in the private storage (never in MEDIA_ROOT)."""

    try:
        upload.seek(0)
    except Exception:  # pragma: no cover - exotic upload objects
        pass
    website.source_invitation.save(upload.name, upload, save=False)
    website.source_filename = upload.name


@login_required
def review(request, slug: str):
    """Step 2 — confirm (and correct) the extracted wedding details."""

    website = _owned_website(request, slug)
    if request.method == "POST":
        form = WeddingDetailsForm(
            request.POST, instance=website, lang=i18n.get_language(request)
        )
        if form.is_valid():
            form.save()
            _mark_confirmed(website, request.POST)
            messages.success(request, "Wedding details saved.")
            return redirect("websites:themes", slug=website.slug)
    else:
        initial = _suggested_initial(website)
        form = WeddingDetailsForm(
            instance=website, initial=initial, lang=i18n.get_language(request)
        )
    return render(
        request,
        "websites/review.html",
        {
            **_editor_context(request, website, "review"),
            "form": form,
            "groups": _details_groups(form),
            "extracted": website.extracted_fields,
            "warnings": website.extraction_warnings,
        },
    )


def _suggested_initial(website: WeddingWebsite) -> dict:
    """Pre-fill empty fields with the extracted suggestions."""

    initial: dict[str, str] = {}
    for key, payload in website.extracted_fields.items():
        if not isinstance(payload, dict):
            continue
        value = payload.get("value") or ""
        if not value:
            continue
        if key in {"groom_name", "bride_name", "venue_name", "venue_city", "venue_state"}:
            current = getattr(website, key, "") or ""
            if not current:
                initial[key] = value
        elif key in {"wedding_date", "ceremony_time"}:
            current = getattr(website, key, None)
            if not current:
                initial[key] = value
    return initial


def _mark_confirmed(website: WeddingWebsite, posted) -> None:
    """Flag the extracted fields the owner has now reviewed."""

    data = website.extracted_fields
    if not data:
        return
    changed = False
    for key, payload in data.items():
        if not isinstance(payload, dict):
            continue
        payload["confirmed"] = True
        changed = True
    if changed:
        website.extracted_data = data
        website.save(update_fields=["extracted_data", "updated_at"])


# ---------------------------------------------------------------------------
# owner: theme, schedule, photos, customisation
# ---------------------------------------------------------------------------
@login_required
def choose_theme(request, slug: str):
    website = _owned_website(request, slug)
    form = ThemeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        website.theme = form.cleaned_data["theme"]
        if not website.accent_color or not website.theme_config.allows_accent(
            website.accent_color
        ):
            website.accent_color = ""
        website.save(update_fields=["theme", "accent_color", "updated_at"])
        messages.success(request, "Theme updated — your details stayed the same.")
        return redirect("websites:customize", slug=website.slug)
    return render(
        request,
        "websites/themes.html",
        {
            **_editor_context(request, website, "themes"),
            "form": form,
            "selected": website.theme,
        },
    )


@login_required
def events(request, slug: str):
    website = _owned_website(request, slug)
    event = None
    if request.method == "POST":
        if "delete_event" in request.POST:
            event_id = request.POST.get("delete_event")
            target = get_object_or_404(WeddingEvent, pk=event_id, website=website)
            target.delete()
            messages.success(request, "Event removed.")
            return redirect("websites:events", slug=website.slug)

        event_id = request.POST.get("event_id")
        if event_id:
            event = get_object_or_404(WeddingEvent, pk=event_id, website=website)
        form = WeddingEventForm(
            request.POST, instance=event, lang=i18n.get_language(request)
        )
        if form.is_valid():
            saved = form.save(commit=False)
            saved.website = website
            if not saved.order:
                saved.order = website.events.count() + 1
            saved.save()
            messages.success(request, "Event saved.")
            return redirect("websites:events", slug=website.slug)
    else:
        event = None
        edit_id = request.GET.get("edit")
        if edit_id:
            event = get_object_or_404(WeddingEvent, pk=edit_id, website=website)
        form = WeddingEventForm(instance=event, lang=i18n.get_language(request))

    return render(
        request,
        "websites/events.html",
        {
            **_editor_context(request, website, "events"),
            "form": form,
            "editing": event,
            "event_list": website.events.all(),
        },
    )


@login_required
def photos(request, slug: str):
    website = _owned_website(request, slug)
    form = WeddingPhotoForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        photo = form.save(commit=False)
        photo.website = website
        photo.save()
        messages.success(request, "Photo added.")
        return redirect("websites:photos", slug=website.slug)
    return render(
        request,
        "websites/photos.html",
        {
            **_editor_context(request, website, "photos"),
            "form": form,
            "photo_list": website.photos.all(),
        },
    )


@login_required
@require_POST
def photo_delete(request, slug: str, photo_id: int):
    website = _owned_website(request, slug)
    photo = get_object_or_404(WeddingPhoto, pk=photo_id, website=website)
    photo.delete()
    messages.success(request, "Photo removed.")
    return redirect("websites:photos", slug=website.slug)


@login_required
def customize(request, slug: str):
    website = _owned_website(request, slug)
    form = CustomizeForm(
        request.POST or None, instance=website, lang=i18n.get_language(request)
    )
    if request.method == "POST" and form.is_valid():
        accent = (form.cleaned_data.get("accent_color") or "").strip()
        if accent and not website.theme_config.allows_accent(accent):
            form.add_error("accent_color", "This colour is not part of the theme palette.")
        else:
            form.save()
            messages.success(request, "Customisation saved.")
            return redirect("websites:preview", slug=website.slug)
    return render(
        request,
        "websites/customize.html",
        {
            **_editor_context(request, website, "customize"),
            "form": form,
            "toggles": [
                form[name]
                for name in (
                    "show_countdown",
                    "show_story",
                    "show_gallery",
                    "show_family",
                    "show_rsvp",
                    "rsvp_ask_guest_count",
                    "rsvp_ask_message",
                    "show_contact",
                )
                if name in form.fields
            ],
            "accents": website.theme_config.accents,
        },
    )


# ---------------------------------------------------------------------------
# owner: preview, publish, share
# ---------------------------------------------------------------------------
@login_required
def preview(request, slug: str):
    website = _owned_website(request, slug)
    return render(
        request,
        "websites/preview.html",
        {
            **_editor_context(request, website, "preview"),
            "frame_url": reverse("websites:preview_frame", kwargs={"slug": website.slug}),
            "warnings": missing_information(website),
        },
    )


@login_required
def preview_frame(request, slug: str):
    """The microsite rendered for the owner (never public)."""

    website = _owned_website(request, slug)
    response = render(
        request,
        website.theme_config.template,
        _site_context(request, website, is_preview=True),
    )
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


@login_required
def publish(request, slug: str):
    website = _owned_website(request, slug)
    missing = missing_information(website)
    if request.method == "POST":
        if request.POST.get("confirm") != "yes":
            messages.error(request, "Please confirm the publication explicitly.")
            return redirect("websites:publish", slug=website.slug)
        if not website.groom_name or not website.bride_name or not website.wedding_date:
            messages.error(
                request, "Add the couple's names and the wedding date before publishing."
            )
            return redirect("websites:review", slug=website.slug)
        with transaction.atomic():
            website.publish()
        messages.success(request, "Your wedding website is live — share it with guests!")
        return redirect("websites:share", slug=website.slug)

    return render(
        request,
        "websites/publish.html",
        {
            **_editor_context(request, website, "publish"),
            "warnings": missing,
            "share_url": website.public_url(),
        },
    )


@login_required
@require_POST
def unpublish(request, slug: str):
    website = _owned_website(request, slug)
    with transaction.atomic():
        website.unpublish()
    messages.success(request, "The website is offline again (your link is kept).")
    return redirect("websites:dashboard")


@login_required
def share(request, slug: str):
    website = _owned_website(request, slug)
    message = services.share_message(website)
    return render(
        request,
        "websites/share.html",
        {
            **_editor_context(request, website, "publish"),
            "public_url": website.public_url(),
            "share_message": message,
            "whatsapp_url": services.whatsapp_share_url(message),
            "preview_image": services.preview_image(website),
        },
    )


@login_required
def delete(request, slug: str):
    website = _owned_website(request, slug)
    if request.method == "POST":
        if request.POST.get("confirm") != "yes":
            return redirect("websites:dashboard")
        website.delete()
        messages.success(request, "Wedding website deleted.")
        return redirect("websites:dashboard")
    return render(
        request,
        "websites/delete.html",
        {**_editor_context(request, website, "publish")},
    )


@login_required
def invitation_source(request, slug: str):
    """Owner-only download of the original invitation (never public)."""

    website = _owned_website(request, slug)
    if not website.source_invitation:
        raise Http404("No invitation file was uploaded.")
    response = HttpResponse(
        website.source_invitation.read(), content_type="application/octet-stream"
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{website.source_filename or "invitation"}"'
    )
    response["X-Robots-Tag"] = "noindex, nofollow"
    return response


# ---------------------------------------------------------------------------
# owner: RSVP management
# ---------------------------------------------------------------------------
@login_required
def rsvps(request, slug: str):
    website = _owned_website(request, slug)
    return render(
        request,
        "websites/rsvps.html",
        {
            **_editor_context(request, website, "publish"),
            "rsvp_list": website.rsvps.all(),
            "attending_count": website.attending_count,
        },
    )


@login_required
def rsvps_csv(request, slug: str):
    website = _owned_website(request, slug)
    response = HttpResponse(services.rsvp_csv(website), content_type="text/csv")
    response["Content-Disposition"] = (
        f'attachment; filename="rsvps-{website.slug}.csv"'
    )
    return response


@login_required
@require_POST
def rsvp_delete(request, slug: str, rsvp_id: int):
    website = _owned_website(request, slug)
    rsvp = get_object_or_404(WeddingRSVP, pk=rsvp_id, website=website)
    rsvp.delete()
    messages.success(request, "Response removed.")
    return redirect("websites:rsvps", slug=website.slug)


# ---------------------------------------------------------------------------
# public
# ---------------------------------------------------------------------------
def public_site(request, slug: str):
    """The published wedding microsite."""

    website = get_object_or_404(
        WeddingWebsite, slug=slug, status=WeddingWebsite.STATUS_PUBLISHED
    )
    website.increment_views()
    context = _site_context(request, website)
    context["rsvp_form"] = PublicRSVPForm(
        initial={"website": website.pk, "started_at": time.time()},
        lang=website.language,
    )
    response = render(request, website.theme_config.template, context)
    return response


@require_POST
def public_rsvp(request, slug: str):
    """Guest RSVP submission (rate limited, honeypot + time trap protected)."""

    website = get_object_or_404(
        WeddingWebsite, slug=slug, status=WeddingWebsite.STATUS_PUBLISHED
    )
    if not website.show_rsvp:
        raise Http404("RSVP is closed for this wedding.")

    ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", ""))
    ip = ip.split(",")[0].strip()
    if _is_rate_limited(
        f"rsvp:{website.pk}:{ip}",
        limit=settings.WEDDING_RSVP_RATE_LIMIT,
        window=settings.WEDDING_RSVP_RATE_WINDOW,
    ):
        messages.error(request, "Too many responses from this device. Please try later.")
        return redirect("websites:public_site", slug=website.slug)

    form = PublicRSVPForm(request.POST, lang=website.language)
    if form.is_valid():
        with transaction.atomic():
            rsvp, created = WeddingRSVP.objects.update_or_create(
                website=website,
                guest_phone=form.cleaned_data["guest_phone"],
                defaults={
                    "guest_name": form.cleaned_data["guest_name"],
                    "attending": form.cleaned_data["attending"],
                    "guest_count": form.cleaned_data["guest_count"],
                    "message": form.cleaned_data["message"],
                },
            )
        if not website.rsvp_ask_guest_count:
            rsvp.guest_count = 1
            rsvp.save(update_fields=["guest_count"])
        if not website.rsvp_ask_message:
            rsvp.message = ""
            rsvp.save(update_fields=["message"])
        if created:
            messages.success(request, "Thank you! Your response has been recorded.")
        else:
            messages.info(request, "Thank you! Your response has been updated.")
    else:
        messages.error(request, "Please check the form and try again.")

    return redirect("websites:public_site", slug=website.slug)


def missing_information(website: WeddingWebsite) -> list[str]:
    """Sections that would look empty on the public site."""

    missing: list[str] = []
    if not (website.groom_name and website.bride_name):
        missing.append("Couple names")
    if not website.wedding_date:
        missing.append("Wedding date")
    if not website.venue_name and not website.venue_address:
        missing.append("Venue")
    if not website.events.exists():
        missing.append("Event schedule")
    if not website.photos.exists():
        missing.append("Photographs")
    if not website.introduction and not website.welcome_message:
        missing.append("Welcome message")
    return missing
