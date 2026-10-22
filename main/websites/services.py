"""Helper services for wedding websites (sharing, maps, CSV, thumbnails)."""

from __future__ import annotations

import csv
import io
from urllib.parse import quote, urlencode

from django.conf import settings

from . import themes


def whatsapp_share_url(text: str, phone: str = "") -> str:
    """Properly URL-encoded WhatsApp share link (never auto-sends anything)."""

    phone = (phone or "").replace("+", "").strip()
    if phone:
        return f"https://wa.me/{quote(phone)}?{urlencode({'text': text})}"
    return f"https://wa.me/?{urlencode({'text': text})}"


def share_message(website) -> str:
    """Default share text for a wedding website."""

    title = website.display_title or "Our Wedding"
    if website.wedding_date:
        title = f"{title} · {website.wedding_date.strftime('%d %B %Y')}"
    return f"{title} — आपका आमंत्रण: {website.public_url()}"


def maps_directions_url(venue_name: str = "", address: str = "", city: str = "") -> str:
    """Google Maps directions URL for a venue (no API key needed)."""

    destination = ", ".join(part for part in (venue_name, address, city) if part)
    if not destination:
        return ""
    return f"https://www.google.com/maps/dir/?api=1&destination={quote(destination)}"


def maps_place_url(venue_name: str = "", address: str = "", city: str = "") -> str:
    """Google Maps place link for a venue."""

    query = ", ".join(part for part in (venue_name, address, city) if part)
    if not query:
        return ""
    return f"https://www.google.com/maps/search/?api=1&query={quote(query)}"


def rsvp_csv(website) -> str:
    """CSV export of the RSVP list (owner only)."""

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        ["Guest name", "Phone", "Attending", "Guests", "Message", "Submitted at"]
    )
    for rsvp in website.rsvps.all():
        writer.writerow(
            [
                rsvp.guest_name,
                rsvp.guest_phone,
                "Yes" if rsvp.attending else "No",
                rsvp.guest_count,
                rsvp.message,
                rsvp.created_at.astimezone().strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return buffer.getvalue()


def preview_image(website):
    """Best public preview image for social sharing (may be ``None``)."""

    photo = website.photos.filter(kind="couple").first() or website.photos.first()
    if photo is None:
        return None
    try:
        return photo.image.url
    except Exception:  # pragma: no cover - storage without a URL
        return None


def theme_palette(code: str) -> list[str]:
    return list(themes.get_theme(code).accents)


def public_site_context(website) -> dict:
    """Everything the public template needs, in one place."""

    theme = website.theme_config
    venue_link = website.venue_maps_url or maps_place_url(
        website.venue_name, website.venue_address, website.venue_city
    )
    directions = maps_directions_url(
        website.venue_name, website.venue_address, website.venue_city
    )
    return {
        "website": website,
        "theme": theme,
        "venue_link": venue_link,
        "directions_url": directions,
        "site_url": website.public_url(),
        "canonical_url": website.public_url(),
        "preview_image": preview_image(website),
        "site_url_origin": settings.DEFAULT_SITE_URL,
    }
