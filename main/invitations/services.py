"""Business helpers: WhatsApp message generation, share links, maps links."""

from __future__ import annotations

from urllib.parse import quote

from django.conf import settings
from django.urls import reverse

from . import bihari

# Pre-built Bihari WhatsApp templates (design.md §5.A).  Each dialect keeps
# the respectful "सहर्ष निमंत्रण / दर्शनाभिलाषी" tone of the region.
WHATSAPP_TEMPLATES = {
    "HI": (
        "ॐ श्री गणेशाय नमः ॥\n"
        "स्नेही आत्मीय जन, श्री {family_head} ({native_place}) के परिवार की तरफ से "
        "सहर्ष निमंत्रण।\n"
        "हमारे {groom} संग {bride} के विवाह उत्सव (\"विवाह बंधन\") में आपकी उपस्थिति "
        "सादर प्रार्थनीय है।\n"
        "वेन्यू लोकेशन, {functions} का पूरा विवरण देखने के लिए नीचे दिए लिंक पर क्लिक करें:\n"
        "{link}\n"
        "दर्शनाभिलाषी: समस्त {family_short} परिवार"
    ),
    "MAI": (
        "ॐ श्री गणेशाय नमः ॥\n"
        "स्नेही आत्मीय जन, श्री {family_head} ({native_place}) के परिवार सँ सहर्ष निमंत्रण।\n"
        "हमर {groom} संग {bride} के विवाह उत्सव (\"विवाह बंधन\") में अहाँक उपस्थिति "
        "सादर प्रार्थनीय छवि।\n"
        "वेन्यू लोकेशन, {functions} के पूरा विवरण देखी खातिर नीचे दिए लिंक पर क्लिक करी:\n"
        "{link}\n"
        "दर्शनाभिलाषी: समस्त {family_short} परिवार"
    ),
    "BHO": (
        "ॐ श्री गणेशाय नमः ॥\n"
        "स्नेही आत्मीय जन, श्री {family_head} ({native_place}) के परिवार से सहर्ष निमंत्रण।\n"
        "हमर {groom} संग {bride} के विवाह उत्सव (\"विवाह बंधन\") में आपके उपस्थिति "
        "सादर प्रार्थनीय छे।\n"
        "वेन्यू लोकेशन, {functions} के पूरा विवरण देखी खातिर नीचे दिए लिंक पर क्लिक करी:\n"
        "{link}\n"
        "दर्शनाभिलाषी: समस्त {family_short} परिवार"
    ),
    "EN": (
        "Om Shri Ganeshay Namah ||\n"
        "Dear friends and family, Shri {family_head} ({native_place}) of the family "
        "cordially invite you to the wedding celebrations of {groom} and {bride}.\n"
        "Your presence is requested at every function — {functions}.\n"
        "View the venue, timings and directions here:\n"
        "{link}\n"
        "Regards, the {family_short} family"
    ),
}


def event_share_url(event, guest_tag: str | None = None) -> str:
    """Absolute URL of the public invitation, optionally tagged for a guest."""

    path = reverse("invitations:event_detail", kwargs={"slug": event.slug})
    url = f"{settings.DEFAULT_SITE_URL.rstrip('/')}{path}"
    if guest_tag:
        url = f"{url}?guest={quote(guest_tag)}"
    return url


def function_summary(event, limit: int = 4) -> str:
    names = [f.function_name for f in event.functions_in_order()[:limit]]
    if not names:
        return ""
    if len(names) > limit:
        return ", ".join(names[:limit]) + " …"
    return ", ".join(names)


def build_whatsapp_message(event, guest_tag: str | None = None) -> str:
    """Render the pre-written Bihari WhatsApp invitation for ``event``."""

    template = WHATSAPP_TEMPLATES.get(event.primary_language, WHATSAPP_TEMPLATES["HI"])
    family_head = (event.family_head_name or "").strip()
    # "Shri Ramakant Roy" -> "Ramakant Roy" for the short family sign-off.
    family_short = family_head
    for prefix in ("श्री ", "श्रीमती ", "श्रीमान् ", "Sri ", "Smt. "):
        if family_short.startswith(prefix):
            family_short = family_short[len(prefix) :]
            break
    family_short = family_short.split()[-1] if family_short else "पारिवारिक"

    context = {
        "family_head": family_head or "परिवार",
        "family_short": family_short,
        "native_place": event.native_place or "बिहार",
        "groom": event.groom_name,
        "bride": event.bride_name,
        "functions": function_summary(event) or "विवाह संस्कार",
        "link": event_share_url(event, guest_tag),
    }
    return template.format(**context)


def whatsapp_link(message: str, phone: str | None = None) -> str:
    """wa.me deep link that opens WhatsApp with the message prefilled."""

    base = "https://wa.me/"
    if phone:
        digits = "".join(ch for ch in phone if ch.isdigit())
        base += digits
    return f"{base}?text={quote(message)}"


def google_maps_link(query: str) -> str:
    return "https://www.google.com/maps/search/?api=1&query=" + quote(query)


def template_preview_seed(event) -> dict:
    """Colour + typography tokens for the chosen theme (used by the CSS vars)."""

    preset = bihari.THEME_STYLE_PRESETS.get(event.theme_style, {})
    return {
        "primary": preset.get("primary", bihari.PALETTE["sindoor"]),
        "secondary": preset.get("secondary", bihari.PALETTE["ochre"]),
        "accent": preset.get("accent", bihari.PALETTE["teal"]),
        "background": preset.get("background", bihari.PALETTE["parchment"]),
        "sindoor": bihari.PALETTE["sindoor"],
        "genda": bihari.PALETTE["genda"],
        "gold": bihari.PALETTE["gold"],
        "ochre": bihari.PALETTE["ochre"],
        "teal": bihari.PALETTE["teal"],
        "terracotta": bihari.PALETTE["terracotta"],
        "imperial_blue": bihari.PALETTE["imperial_blue"],
    }
