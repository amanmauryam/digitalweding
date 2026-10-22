"""Wedding-website themes.

Every theme is a complete *website* skin (not an invitation card): a colour
system, a typography pairing, a decorative motif and a small set of layout
tweaks.  All of them render the very same wedding information — the theme
only decides how it is presented.

The palette lives here (not in the database) so that a theme can be added
without a migration, and so the accent picker can only ever offer colours
that belong to the selected design system.
"""

from __future__ import annotations

from dataclasses import dataclass, field

THEME_ROYAL_INDIAN = "royal_indian"
THEME_MODERN_MINIMAL = "modern_minimal"
THEME_FLORAL_ROMANCE = "floral_romance"
THEME_MITHILA_HERITAGE = "mithila_heritage"
THEME_BIHAR_TRADITIONAL = "bihar_traditional"
THEME_CONTEMPORARY_LUXURY = "contemporary_luxury"

DEFAULT_THEME = THEME_ROYAL_INDIAN


@dataclass(frozen=True)
class Theme:
    code: str
    name: str
    name_hi: str
    tagline: str
    description: str
    colors: dict[str, str]
    fonts: dict[str, str]
    accents: tuple[str, ...]
    motif: str = "none"
    radius: str = "18px"
    features: tuple[str, ...] = field(default_factory=tuple)

    @property
    def heading_font(self) -> str:
        return self.fonts["heading"]

    @property
    def body_font(self) -> str:
        return self.fonts["body"]

    @property
    def template(self) -> str:
        """Template rendering this theme's public microsite."""

        return f"websites/themes/{self.code}/site.html"

    def allows_accent(self, colour: str) -> bool:
        return (colour or "").lower() in {item.lower() for item in self.accents}

    def as_dict(self) -> dict:
        return {
            "code": self.code,
            "name": self.name,
            "name_hi": self.name_hi,
            "tagline": self.tagline,
            "description": self.description,
            "colors": dict(self.colors),
            "fonts": dict(self.fonts),
            "accents": list(self.accents),
            "motif": self.motif,
            "radius": self.radius,
            "features": list(self.features),
        }


THEMES: tuple[Theme, ...] = (
    Theme(
        code=THEME_ROYAL_INDIAN,
        name="Royal Indian",
        name_hi="शाही भारतीय",
        tagline="Maroon, ivory and muted gold",
        description=(
            "Deep maroon velvet with ivory parchment and antique gold — the "
            "classic Banarasi wedding palette."
        ),
        colors={
            "bg": "#2b0a12",
            "surface": "#3d1019",
            "surface_alt": "#4a1622",
            "text": "#f8ecd8",
            "muted": "#d9bd99",
            "accent": "#d4af37",
            "accent_soft": "#8c1c2b",
            "border": "#d4af37",
        },
        fonts={
            "heading": "'Cinzel', 'Rozha One', 'Noto Sans Devanagari', serif",
            "body": "'Tiro Devanagari Hindi', 'Noto Sans Devanagari', serif",
        },
        accents=("#d4af37", "#eab308", "#b22222", "#f5deb3"),
        motif="filigree",
        radius="14px",
        features=("countdown", "gold-borders"),
    ),
    Theme(
        code=THEME_MODERN_MINIMAL,
        name="Modern Minimal",
        name_hi="आधुनिक मिनिमल",
        tagline="Warm white, refined type, generous space",
        description=(
            "A quiet, editorial layout with warm white surfaces, a single "
            "accent and a lot of breathing room."
        ),
        colors={
            "bg": "#faf7f2",
            "surface": "#ffffff",
            "surface_alt": "#f2ece3",
            "text": "#2b2b2b",
            "muted": "#7a7269",
            "accent": "#b08968",
            "accent_soft": "#ede0d1",
            "border": "#e2d8ca",
        },
        fonts={
            "heading": "'Playfair Display', 'Noto Sans Devanagari', serif",
            "body": "'Noto Sans Devanagari', 'Tiro Devanagari Hindi', sans-serif",
        },
        accents=("#b08968", "#7f5539", "#9a8c98", "#495057"),
        motif="none",
        radius="6px",
        features=("countdown",),
    ),
    Theme(
        code=THEME_FLORAL_ROMANCE,
        name="Floral Romance",
        name_hi="फूलों का रोमांस",
        tagline="Soft blush with botanical details",
        description=(
            "Blush and sage tones, fine botanical line work and an elegant "
            "script-like rhythm for the couple's names."
        ),
        colors={
            "bg": "#fdf4f1",
            "surface": "#ffffff",
            "surface_alt": "#f7e6e0",
            "text": "#4a2f33",
            "muted": "#9a7b7b",
            "accent": "#c98a92",
            "accent_soft": "#f2d7d5",
            "border": "#e8c9c6",
        },
        fonts={
            "heading": "'Playfair Display', 'Yatra One', serif",
            "body": "'Tiro Devanagari Hindi', 'Noto Sans Devanagari', serif",
        },
        accents=("#c98a92", "#a4b494", "#d9a5b0", "#8c6b6b"),
        motif="botanical",
        radius="20px",
        features=("countdown", "botanical"),
    ),
    Theme(
        code=THEME_MITHILA_HERITAGE,
        name="Mithila Heritage",
        name_hi="मिथिला विरासत",
        tagline="Madhubani borders and motifs",
        description=(
            "Original Madhubani-inspired borders, lotus and peacock motifs "
            "drawn as inline SVG around a warm parchment canvas."
        ),
        colors={
            "bg": "#f7efdc",
            "surface": "#fdf7e8",
            "surface_alt": "#efe0bf",
            "text": "#33241a",
            "muted": "#7b6146",
            "accent": "#9a3412",
            "accent_soft": "#d8b56b",
            "border": "#9a3412",
        },
        fonts={
            "heading": "'Rozha One', 'Yatra One', serif",
            "body": "'Tiro Devanagari Hindi', 'Noto Sans Devanagari', serif",
        },
        accents=("#9a3412", "#0d9488", "#b22222", "#c5a059"),
        motif="madhubani",
        radius="10px",
        features=("countdown", "madhubani-borders"),
    ),
    Theme(
        code=THEME_BIHAR_TRADITIONAL,
        name="Traditional Bihar Wedding",
        name_hi="पारंपरिक बिहार शादी",
        tagline="Regional craft with a modern layout",
        description=(
            "Terracotta, turmeric and peacock green with woven-textile "
            "accents — folk craft on a clean modern grid."
        ),
        colors={
            "bg": "#fdf6ec",
            "surface": "#ffffff",
            "surface_alt": "#f7e4cd",
            "text": "#3b2410",
            "muted": "#8a5a2b",
            "accent": "#c2410c",
            "accent_soft": "#eab308",
            "border": "#e0b183",
        },
        fonts={
            "heading": "'Yatra One', 'Rozha One', serif",
            "body": "'Tiro Devanagari Hindi', 'Noto Sans Devanagari', serif",
        },
        accents=("#c2410c", "#eab308", "#0d9488", "#b22222"),
        motif="weave",
        radius="12px",
        features=("countdown", "weave"),
    ),
    Theme(
        code=THEME_CONTEMPORARY_LUXURY,
        name="Contemporary Luxury",
        name_hi="आधुनिक विलासिता",
        tagline="Deep colour, restrained effects",
        description=(
            "Ink-blue and gold with wide tracking, hairline rules and a "
            "gently luminous hero."
        ),
        colors={
            "bg": "#0b1b2b",
            "surface": "#12283c",
            "surface_alt": "#17324a",
            "text": "#eef4f8",
            "muted": "#9fb6c6",
            "accent": "#c9a227",
            "accent_soft": "#1f3f5c",
            "border": "#c9a227",
        },
        fonts={
            "heading": "'Cinzel', 'Playfair Display', serif",
            "body": "'Noto Sans Devanagari', 'Tiro Devanagari Hindi', sans-serif",
        },
        accents=("#c9a227", "#e0b84c", "#7f9cb5", "#b08d57"),
        motif="hairline",
        radius="4px",
        features=("countdown", "hairlines"),
    ),
)

THEMES_BY_CODE: dict[str, Theme] = {theme.code: theme for theme in THEMES}


def get_theme(code: str | None) -> Theme:
    """Return the theme for ``code`` falling back to the default theme."""

    return THEMES_BY_CODE.get((code or "").strip(), THEMES_BY_CODE[DEFAULT_THEME])


def theme_choices() -> list[tuple[str, str]]:
    """Choices for the ``theme`` model field."""

    return [(theme.code, theme.name) for theme in THEMES]


def theme_codes() -> list[str]:
    return [theme.code for theme in THEMES]
