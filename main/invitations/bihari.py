"""Bihari wedding domain constants.

Single source of truth for the function schema (design.md §3), the cultural
colour palette (§2) and the visual theme styles used by the invitation
templates.
"""

from __future__ import annotations

from collections import OrderedDict

# ---------------------------------------------------------------------------
# §2 — Bihari cultural colour palette
# ---------------------------------------------------------------------------
PALETTE = {
    "sindoor": "#800020",       # Sindoor Red / Crimson — primary bridal shade
    "crimson": "#B22222",       # Vermillion Red — Dwar Puja
    "genda": "#EAB308",         # Genda Phool Yellow / Haldi Gold
    "gold": "#D4AF37",          # Royal Gold — Jaimala
    "ochre": "#C5A059",         # Mithila Silk Ochre — parchment background
    "teal": "#0D9488",          # Peacock Teal — Kohbar Ghar
    "peacock_dark": "#064E3B",  # Deep peacock green
    "terracotta": "#9A3412",    # Ganga Clay Terracotta — Matkor
    "imperial_blue": "#1E3A8A",  # Imperial Blue — Preeti Bhoj
    "parchment": "#FBF1DC",     # Madhubani card background
    "ink": "#2B1A12",           # Deep kalam ink
}

# ---------------------------------------------------------------------------
# §3 — Bihari function & ritual schema mapping
# ---------------------------------------------------------------------------
FUNCTION_TEMPLATES = OrderedDict(
    (
        (
            "TILAK",
            {
                "code": "TILAK",
                "bihari_name": "Tilakotsav",
                "devanagari": "तिलकोत्सव",
                "accent": PALETTE["sindoor"],
                "folk_music": "Mangal Dhwani",
                "music_slug": "mangal-dhwani",
                "icon": "tilak",
                "blurb": {
                    "hi": "शुभ गंगा निकसन, सिंदूर-चंदन विधि और शुभ लाभ की प्रार्थना।",
                    "mai": "शुभ गंगा निकसन, सिंदूर-चंदन विधि आ शुभ लाभ क प्रार्थना।",
                    "bho": "शुभ गंगा निकसन, सिंदूर-चंदन विधी आ शुभ लाभ के प्रार्थना।",
                    "en": "Holy Ganga ritual, Sindur-chandan ceremony and prayers for a good beginning.",
                },
            },
        ),
        (
            "MATKOR",
            {
                "code": "MATKOR",
                "bihari_name": "Matkor & Sacred Clay Rite",
                "devanagari": "माटकोर",
                "accent": PALETTE["terracotta"],
                "folk_music": "Matkor Folk Songs",
                "music_slug": "matkor-folk",
                "icon": "matkor",
                "blurb": {
                    "hi": "पवित्र मिट्टी से माटकोर निकालकर शुभ कार्य का शुभारंभ।",
                    "mai": "पवित्र माटी सँ माटकोर निकालि शुभ कार्य के शुभारंभ।",
                    "bho": "पवित्र माटी से माटकोर निकालि शुभ काम के शुभारंभ।",
                    "en": "Drawing sacred clay from the ground to inaugurate every auspicious task.",
                },
            },
        ),
        (
            "HALDI",
            {
                "code": "HALDI",
                "bihari_name": "Haldi-Ubtan & Imli Ghotai",
                "devanagari": "हल्दी-उबटन",
                "accent": PALETTE["genda"],
                "folk_music": "Vivah Haldi Geet",
                "music_slug": "vivah-haldi-geet",
                "icon": "haldi",
                "blurb": {
                    "hi": "हल्दी-उबटन और इमली घोटाई की रंगीन सुखमय विधि।",
                    "mai": "हल्दी-उबटन आ इमली घोटाई के रंगीन सुखमय विधि।",
                    "bho": "हल्दी-उबटन आ इमली घोटाई के रंगीन सुखमय विधि।",
                    "en": "The joyous turmeric and imli ceremony full of colour and laughter.",
                },
            },
        ),
        (
            "PARICHAWAN",
            {
                "code": "PARICHAWAN",
                "bihari_name": "Dwar Puja & Parichhawan",
                "devanagari": "द्वार पूजा",
                "accent": PALETTE["crimson"],
                "folk_music": "Shehnai & Nagada",
                "music_slug": "shehnai-nagada",
                "icon": "dwar-puja",
                "blurb": {
                    "hi": "द्वार पूजा, नगाड़ा-शहनाई और शुभ प्रवेश का आयोजन।",
                    "mai": "द्वार पूजा, नगाड़ा-शहनाई आ शुभ प्रवेश के आयोजन।",
                    "bho": "द्वार पूजा, नगाड़ा-शहनाई आ शुभ प्रवेश के आयोजन।",
                    "en": "Door worship with nagada and shehnai heralding the auspicious arrival.",
                },
            },
        ),
        (
            "JAIMALA",
            {
                "code": "JAIMALA",
                "bihari_name": "Jaimala & Subh Vivah",
                "devanagari": "जयमाला व शुभ विवाह",
                "accent": PALETTE["gold"],
                "folk_music": "Vedic Shloka",
                "music_slug": "vedic-shloka",
                "icon": "jaimala",
                "blurb": {
                    "hi": "वैदिक मंत्रों के साथ जयमाला और शुभ विवाह की स्थापना।",
                    "mai": "वैदिक मंत्र के साथ जयमाला आ शुभ विवाह के स्थापना।",
                    "bho": "वैदिक मंत्र के साथ जयमाला आ शुभ विवाह के स्थापना।",
                    "en": "The exchange of garlands and the sacred union accompanied by Vedic hymns.",
                },
            },
        ),
        (
            "KOHBAR",
            {
                "code": "KOHBAR",
                "bihari_name": "Kohbar Pujan",
                "devanagari": "कोहबर पूजन",
                "accent": PALETTE["teal"],
                "folk_music": "Kohbar Folk Geet",
                "music_slug": "kohbar-geet",
                "icon": "kohbar",
                "blurb": {
                    "hi": "कोहबर गृह पूजन — कोहबर की दीवार पर मधुबनी कला की आकृति।",
                    "mai": "कोहबर गृह पूजन — कोहबर के दीवार पर मधुबनी कला के आकृति।",
                    "bho": "कोहबर घर पूजन — कोहबर के दीवार पर मधुबनी कला के आकृति।",
                    "en": "Housewarming worship with Madhubani motifs painted on the Kohbar walls.",
                },
            },
        ),
        (
            "RECEPTION",
            {
                "code": "RECEPTION",
                "bihari_name": "Preeti Bhoj / Samdhan Bhent",
                "devanagari": "प्रीतिभोज",
                "accent": PALETTE["imperial_blue"],
                "folk_music": "Light Classical Flute",
                "music_slug": "flute-classical",
                "icon": "preeti-bhoj",
                "blurb": {
                    "hi": "प्रीतिभोज — बैंसुरी, नगाड़ा और प्रीतिभोज का आयोजन।",
                    "mai": "प्रीतिभोज — बाँसुरी, नगाड़ा आ प्रीतिभोज के आयोजन।",
                    "bho": "प्रीतिभोज — बाँसुरी, नगाड़ा आ प्रीतोज के आयोजन।",
                    "en": "The community feast with flute, nagada and shared celebration.",
                },
            },
        ),
    )
)

FUNCTION_CODES = tuple(FUNCTION_TEMPLATES.keys())

# ---------------------------------------------------------------------------
# Template theme styles (design.md §4)
# ---------------------------------------------------------------------------
THEME_STYLES = [
    ("MITHILA", "Mithila & Madhubani Art Style"),
    ("ROYAL_RAJ", "Royal Rajputana / Jamindari Theme"),
    ("MODERN_BIHARI", "Modern Minimalist Bihari Accent"),
    ("BHOJPURI_FOLK", "Bhojpuri Cultural Aesthetic"),
]

THEME_STYLE_PRESETS = {
    "MITHILA": {
        "primary": PALETTE["sindoor"],
        "secondary": PALETTE["ochre"],
        "accent": PALETTE["teal"],
        "background": PALETTE["parchment"],
    },
    "ROYAL_RAJ": {
        "primary": PALETTE["sindoor"],
        "secondary": PALETTE["gold"],
        "accent": PALETTE["crimson"],
        "background": "#FCF7E8",
    },
    "MODERN_BIHARI": {
        "primary": PALETTE["sindoor"],
        "secondary": PALETTE["terracotta"],
        "accent": PALETTE["peacock_dark"],
        "background": "#FFFDF8",
    },
    "BHOJPURI_FOLK": {
        "primary": PALETTE["terracotta"],
        "secondary": PALETTE["genda"],
        "accent": PALETTE["teal"],
        "background": "#FDF4E3",
    },
}

# ---------------------------------------------------------------------------
# Invitation categories seeded by default
# ---------------------------------------------------------------------------
DEFAULT_CATEGORIES = [
    ("Biyah (Wedding)", "biyah"),
    ("Chhath Puja", "chhath-puja"),
    ("Griha Pravesh", "griha-pravesh"),
    ("Mundan", "mundan"),
    ("Sangeet", "sangeet"),
    ("Other Sanskar", "other-sanskar"),
]


def function_options() -> list[tuple[str, str]]:
    """Choice list for ``EventFunction.function_code``."""

    return [
        (code, f"{data['devanagari']} — {data['bihari_name']}")
        for code, data in FUNCTION_TEMPLATES.items()
    ]


def get_function(code: str) -> dict:
    return FUNCTION_TEMPLATES.get(code, FUNCTION_TEMPLATES["TILAK"])
