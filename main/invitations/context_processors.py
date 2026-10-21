from django.conf import settings

from . import bihari


def site_context(request):
    """Brand + support details available in every template."""

    return {
        "dw_support_whatsapp": settings.SUPPORT_WHATSAPP,
        "dw_support_email": settings.SUPPORT_EMAIL,
        "dw_site_url": settings.DEFAULT_SITE_URL,
        "dw_palette": bihari.PALETTE,
        "dw_audio_default_paused": settings.AUDIO_DEFAULT_PAUSED,
        "dw_google_fonts": (
            "https://fonts.googleapis.com/css2?"
            "family=Cinzel:wght@500;700&"
            "family=Playfair+Display:ital,wght@0,500;0,700;1,500&"
            "family=Rozha+One&"
            "family=Tiro+Devanagari+Hindi:ital@0;1&"
            "family=Yatra+One&"
            "family=Noto+Sans+Devanagari:wght@400;500;700&display=swap"
        ),
    }


def language_context(request):
    """Dialect context: active language, switcher metadata and a ``t`` helper."""

    from . import i18n

    lang = i18n.get_language(request)
    request.LANGUAGE_CODE = lang

    def t(key: str) -> str:
        return i18n.get_string(key, lang)

    return {
        "dw_lang": lang,
        "dw_lang_meta": i18n.LANG_META,
        "dw_active_lang": next(
            (item for item in i18n.LANG_META if item["code"] == lang), i18n.LANG_META[0]
        ),
        "t": t,
    }
