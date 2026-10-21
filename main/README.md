# DigitalWedding · डिजिटल निमंत्रण

बिहार की परंपरा और आधुनिकता का सुंदर मिलन — Django 5 पर बना मुफ़्त डिजिटल वेडिंग इन्विटेशन प्लेटफ़ॉर्म जो मैथिली, भोजपुरी, हिंदी और अंग्रेज़ी में बात करता है।

> Full product spec: [`../design.md`](../design.md)

## Features

| क्षेत्र | विवरण |
| --- | --- |
| सात बिहारी संस्कार | तिलकोत्सव, माटकोर, हल्दी, द्वार पूजा, जयमाला, कोहबर, प्रीतिभोज — each with its own folk-music accent colour |
| चार भाषाएँ | हिंदी · मैथिली · भोजपुरी · English (cookie based, no reload) |
| कोहबर द्वार | Interactive Madhubani door that opens on click and plays a WebAudio shehnai |
| लाइव कस्टमाइज़र | Live preview card inside the event editor — names, date, shloka and theme accent update as you type |
| WhatsApp साझा करें | Dialect-specific WhatsApp message + `wa.me` deep link, copy-link button |
| RSVP + आशीर्वाद | HTMX forms for Aayenge / Sneh Sahit Kshama, virtual पान-लड्डू blessing badge |
| लीड कैप्चर | "Send me my customised invitation" free-tier lead form |
| Django admin | Themes, events, functions, RSVPs, blessings and leads |

## Tech stack

- Django 5.2 · Python 3.14
- PostgreSQL (SQLite fallback for local dev)
- Tailwind CSS 4 (Node build → `static/css/app.css`), Alpine.js 3, HTMX 1.9
- Pillow (image fields), `psycopg` 3, `python-dotenv`

## Front-end build (Node + Tailwind)

Tailwind is compiled locally — no CDN runtime, so pages are fast on 4G and work offline.

```powershell
cd main
npm install          # once
npm run build        # production build → static/css/app.css (minified)
npm run dev          # watch mode: rebuilds on every template change
```

- Source of truth: `src/styles/app.css` (Tailwind v4 CSS-first config: `@theme` tokens, `@source` paths, `@layer components` design system).
- Output: `static/css/app.css` (committed so the app runs even without Node installed).
- Breakpoints: `xs` 26rem (small phones) · `sm` 40rem · `md` 48rem (tablet) · `lg` 64rem (laptop).

### Responsive rules

Every page is mobile-first and adapts at `xs` → `sm` → `md` → `lg`:

| Area | Phone | Tablet | Laptop |
| --- | --- | --- | --- |
| Top bar | logo + current-dialect chip, links inside a hamburger drawer | logo + full dialect switcher, links inside a drawer | logo + dialect switcher, links inline |
| Hero / preview | stacked, 1 column | stacked | 2 columns (`md:grid-cols-[1.1fr_0.9fr]`) |
| Event editor | form over preview | side-by-side (260px preview) | side-by-side (320px preview) |
| Ritual timeline | single column | single column | single column, wider cards |
| RSVP / blessing | stacked | stacked | 2 columns |
| Guest table | horizontal scroll (`min-w-[560px]`) | scroll | fits |
| Buttons | full-width blocks | inline | inline |
| Type scale | `text-xl`–`text-3xl` | `text-2xl`–`text-4xl` | `text-3xl`–`text-5xl` |

CSS-level tweaks live in `src/styles/app.css`: smaller card padding, 16px inputs (no iOS zoom), 44px tap targets, compact blessing badge and reduced motion support.

### Navigation bar

- The header is `sticky top-0` on every page, so the brand, dialect switcher and menu are always one tap away.
- Below the laptop breakpoint (`lg`) a 44px hamburger button opens a full-width drawer with 48px tap targets; the drawer also carries the dialect switcher on phones.
- From `lg` upwards the navigation links sit inline in a second bar and the hamburger is hidden.
- The drawer is an Alpine island (`x-data="{ open: false }"`). Without JavaScript the drawer simply stays expanded, so every link and the dialect switcher remain reachable.

## Dialect-aware forms

Field names, placeholders and help texts are translated too — not just the static copy:

- `invitations/i18n.py` holds three translation tables: `FORM_LABELS`, `FORM_PLACEHOLDERS` and `FORM_HELP` (हिन्दी · मैथिली · भोजपुरी · English).
- `LocalizedFormMixin` swaps them in at form-instantiation time; every view passes `lang=i18n.get_language(request)`, so the labels follow the `dw_lang` cookie immediately.
- Covered forms: login, signup, RSVP, virtual blessing, lead capture, event editor and ritual editor.

## Project layout

```
main/
├── manage.py
├── package.json              # Node build scripts (Tailwind)
├── src/styles/app.css        # Tailwind v4 source (tokens + design system)
├── digitalwedding/          # settings, urls, wsgi, asgi
├── accounts/                # custom User (phone, district), signup/login
├── invitations/             # domain app
│   ├── bihari.py             # palette, ritual schema, theme presets (design.md source of truth)
│   ├── i18n.py              # in-process dialect dictionary (hi/mai/bho/en) + form labels
│   ├── transliterate.py     # Devanagari → Latin slug helper
│   ├── models.py            # InvitationCategory, TemplateTheme, CustomerEvent, EventFunction,
│   │                        # RSVPResponse, GuestBlessing, LeadCapture
│   ├── views.py / forms.py / services.py / admin.py
│   ├── templatetags/dw_tags.py   # {% t "key" %} translation tag, function_blurb filter
│   ├── management/commands/seed_data.py
│   └── tests/               # 60 Django tests
├── templates/               # base + home, event_detail, dashboard, event_form, …
└── static/
    ├── css/app.css          # compiled Tailwind bundle (generated)
    └── js/main.js           # door, shehnai audio, clipboard
```

## Setup

```powershell
cd main
..\.venv\Scripts\Activate.ps1          # or use the interpreter directly
pip install -r requirements.txt
Copy-Item .env.example .env             # adjust DB credentials
python manage.py migrate
python manage.py seed_data --demo       # optional demo invitation
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ — the demo invitation is at `/w/aman-weds-priya-3210/`.

## Environment variables (`.env`)

| Key | Default | Purpose |
| --- | --- | --- |
| `SECRET_KEY` | dev key | Django secret key |
| `DEBUG` | `True` | debug mode |
| `DB_NAME` | *(empty → SQLite)* | Postgres database name (plus `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`) |
| `DATABASE_URL` | *(empty)* | `postgres://user:pass@host:5432/dbname` — overrides the `DB_*` values |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | comma separated hosts |
| `CSRF_TRUSTED_ORIGINS` | local URLs | comma separated origins |
| `SUPPORT_WHATSAPP` / `DW_SUPPORT_WHATSAPP` | `+910000000000` | footer / share support number |
| `SUPPORT_EMAIL` / `DW_SUPPORT_EMAIL` | `hello@digitalwedding.in` | footer support mail |
| `DEFAULT_SITE_URL` | `http://127.0.0.1:8000` | absolute URL used in share links |

## Tests

```powershell
python manage.py test          # 60 tests, all green
python manage.py check
```

## Notes

- Translation is an in-process dictionary (`invitations/i18n.py`) rather than gettext — dialect copy lives next to the domain data and is switched with the `dw_lang` cookie.
- Design tokens (Sindoor / Genda / Ochre / Peacock Teal / Terracotta / Imperial Blue / Parchment) live in the `@theme` block of `src/styles/app.css` and are exposed to Tailwind as `bg-sindoor`, `text-kalam`, `border-ochre`, …
- Art is inline SVG (Madhubani lotus, mandala, kohbar door, laddoo) so pages stay light — no heavy image assets are shipped.
