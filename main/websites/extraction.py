"""Invitation card → wedding details.

Two text sources are supported:

* **Text based PDF** – the embedded text layer is read with ``pypdf``
  (pure Python, no external binary).
* **Images and scanned PDFs** – handled by ``pytesseract``.  Tesseract is an
  *optional* system dependency: when the binary is missing the module raises
  :class:`OCRAvailable` and the caller offers manual entry instead of
  failing the whole flow.

The parser is deliberately conservative.  It never invents a value: a field
is only reported when the text gives a strong signal, and every reported
field carries a confidence score plus the source it came from.  Whatever the
parser is unsure about is listed in ``warnings`` and stays empty in the form.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from datetime import date, time
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image

# ---------------------------------------------------------------------------
# Vocabulary
# ---------------------------------------------------------------------------
MONTHS_EN = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

MONTHS_HI = {
    "जनवरी": 1,
    "फरवरी": 2,
    "फ़रवरी": 2,
    "मार्च": 3,
    "अप्रैल": 4,
    "अप्रेल": 4,
    "मई": 5,
    "जून": 6,
    "जुलाई": 7,
    "अगस्त": 8,
    "सितंबर": 9,
    "सितम्बर": 9,
    "अक्तूबर": 10,
    "अक्टूबर": 10,
    "नवंबर": 11,
    "नवम्बर": 11,
    "दिसंबर": 12,
    "दिसम्बर": 12,
}

MERIDIEM_HI = {
    "सुबह": "am",
    "प्रातः": "am",
    "प्रात:": "am",
    "दोपहर": "pm",
    "मध्याह्न": "pm",
    "शाम": "pm",
    "सायं": "pm",
    "रात": "pm",
}

# Bihar districts + the metros our customers usually migrate to.
CITIES: dict[str, str] = {
    "patna": "Bihar",
    "पटना": "Bihar",
    "muzaffarpur": "Bihar",
    "मुजफ्फरपुर": "Bihar",
    "मुज़फ़्फ़रपुर": "Bihar",
    "gaya": "Bihar",
    "गया": "Bihar",
    "bhagalpur": "Bihar",
    "भागलपुर": "Bihar",
    "darbhanga": "Bihar",
    "दरभंगा": "Bihar",
    "begusarai": "Bihar",
    "बेगूसराय": "Bihar",
    "munger": "Bihar",
    "मुंगेर": "Bihar",
    "chapra": "Bihar",
    "छपरा": "Bihar",
    "purnia": "Bihar",
    "पूर्णिया": "Bihar",
    "saharsa": "Bihar",
    "सहरसा": "Bihar",
    "katihar": "Bihar",
    "कटिहार": "Bihar",
    "nalanda": "Bihar",
    "nalanda ": "Bihar",
    "नालंदा": "Bihar",
    "aurangabad": "Bihar",
    "औरंगाबाद": "Bihar",
    "madhubani": "Bihar",
    "मधुबनी": "Bihar",
    "sitamarhi": "Bihar",
    "सीतामढ़ी": "Bihar",
    "supaul": "Bihar",
    "सुपौल": "Bihar",
    "vaishali": "Bihar",
    "वैशाली": "Bihar",
    "champaran": "Bihar",
    "चम्पारण": "Bihar",
    "samastipur": "Bihar",
    "समस्तीपुर": "Bihar",
    "banka": "Bihar",
    "बांका": "Bihar",
    "jamui": "Bihar",
    "जामुई": "Bihar",
    "sheikhpura": "Bihar",
    "शेखपुरा": "Bihar",
    "buxar": "Bihar",
    "बक्सर": "Bihar",
    "arrah": "Bihar",
    "अररा": "Bihar",
    "jehanabad": "Bihar",
    "जहानाबाद": "Bihar",
    "bhojpur": "Bihar",
    "भोजपुर": "Bihar",
    "gopalganj": "Bihar",
    "गोपालगंज": "Bihar",
    "siwan": "Bihar",
    "सीवान": "Bihar",
    "saran": "Bihar",
    "सारण": "Bihar",
    "hazaribagh": "Jharkhand",
    "हजारीबाग": "Jharkhand",
    "ranchi": "Jharkhand",
    "रांची": "Jharkhand",
    "dhanbad": "Jharkhand",
    "jamshedpur": "Jharkhand",
    "जमशेदपुर": "Jharkhand",
    "delhi": "Delhi",
    "नई दिल्ली": "Delhi",
    "new delhi": "Delhi",
    "mumbai": "Maharashtra",
    "मुंबई": "Maharashtra",
    "pune": "Maharashtra",
    "पुणे": "Maharashtra",
    "bengaluru": "Karnataka",
    "bangalore": "Karnataka",
    "बेंगलुरु": "Karnataka",
    "hyderabad": "Telangana",
    "हैदराबाद": "Telangana",
    "chennai": "Tamil Nadu",
    "चेन्नई": "Tamil Nadu",
    "kolkata": "West Bengal",
    "कोलकाता": "West Bengal",
    "ahmedabad": "Gujarat",
    "अहमदाबाद": "Gujarat",
    "jaipur": "Rajasthan",
    "जयपुर": "Rajasthan",
    "noida": "Uttar Pradesh",
    "गुरुग्राम": "Haryana",
    "gurgaon": "Haryana",
    "lucknow": "Uttar Pradesh",
    "लखनऊ": "Uttar Pradesh",
    "varanasi": "Uttar Pradesh",
    "वाराणसी": "Uttar Pradesh",
    "bhubaneswar": "Odisha",
    "भुबनेश्वर": "Odisha",
    "guwahati": "Assam",
    "गुवाहाटी": "Assam",
    "thiruvananthapuram": "Kerala",
    "coimbatore": "Tamil Nadu",
    "chandigarh": "Punjab",
    "dehradun": "Uttarakhand",
    "goa": "Goa",
}

EVENT_KEYWORDS: list[tuple[str, str, str]] = [
    ("haldi", "Haldi", "हल्दी"),
    ("हल्दी", "Haldi", "हल्दी"),
    ("mehndi", "Mehndi", "मेहंदी"),
    ("महेन्दी", "Mehndi", "मेहंदी"),
    ("मेहंदी", "Mehndi", "मेहंदी"),
    ("sangeet", "Sangeet", "संगीत"),
    ("संगीत", "Sangeet", "संगीत"),
    ("reception", "Reception", "प्रीतिभोज"),
    ("प्रीतिभोज", "Reception", "प्रीतिभोज"),
    ("baraat", "Baraat", "बारात"),
    ("बारात", "Baraat", "बारात"),
    ("gaiyath", "Gaiyath", "गायत्री"),
    ("गायत्री", "Gaiyath", "गायत्री"),
    ("gaiyath puja", "Gaiyath", "गायत्री"),
    ("kanyadaan", "Kanyadaan", "कन्यादान"),
    ("कन्यादान", "Kanyadaan", "कन्यादान"),
    ("vidaai", "Vidaai", "विदाई"),
    ("विदाई", "Vidaai", "विदाई"),
    ("tilak", "Tilak", "तिलकोत्सव"),
    ("तिलकोत्सव", "Tilak", "तिलकोत्सव"),
    ("matkor", "Matkor", "माटकोर"),
    ("माटकोर", "Matkor", "माटकोर"),
]

FAMILY_MARKERS = (
    "s/o",
    "d/o",
    "w/o",
    "पुत्र",
    "पुत्री",
    "पिता",
    "माता",
    "पति",
    "पत्नी",
    "श्री",
    "श्रीमती",
)

STOPWORDS = {
    "सादर",
    "निमंत्रण",
    "आमंत्रण",
    "शुभ",
    "विवाह",
    "invitation",
    "wedding",
    "the",
    "and",
    "weds",
    "son",
    "daughter",
    "daughter's",
    "son's",
    "परिवार",
    "सपरिवार",
    "सादर आमंत्रण",
    "शादी",
}

# Names: keep ASCII capitalised names strict (to avoid swallowing Devanagari)
# and allow Devanagari names separately where appropriate.
_NAME_TOKEN_ASCII = r"[A-Z][A-Za-z'’-]{0,29}"
_NAME_TOKEN_DEV = r"[ऀ-ॿ][ऀ-ॿ'’-]{0,29}"
_NAME_ASCII = rf"{_NAME_TOKEN_ASCII}(?:\s+{_NAME_TOKEN_ASCII}){{0,2}}"
_NAME_DEV = rf"{_NAME_TOKEN_DEV}(?:\s+{_NAME_TOKEN_DEV}){{0,2}}"
_NAME = rf"(?:{_NAME_ASCII}|{_NAME_DEV})"


class ExtractionError(Exception):
    """The invitation could not be read at all."""


class OCRUnavailable(ExtractionError):
    """No OCR engine is installed on this machine."""


@dataclass
class ExtractionResult:
    text: str
    fields: dict[str, dict] = field(default_factory=dict)
    engine: str = ""
    warnings: list[str] = field(default_factory=list)
    pages: int = 0

    def value(self, key: str) -> str:
        payload = self.fields.get(key) or {}
        return str(payload.get("value") or "")

    def as_dict(self) -> dict:
        return {
            "text": self.text,
            "fields": self.fields,
            "engine": self.engine,
            "warnings": self.warnings,
            "pages": self.pages,
        }


# ---------------------------------------------------------------------------
# Text acquisition
# ---------------------------------------------------------------------------
def tesseract_available() -> bool:
    """True when a usable Tesseract installation is present."""

    if not shutil.which("tesseract"):
        return False
    try:  # pragma: no cover - depends on the host machine
        import pytesseract

        pytesseract.get_tesseract_version()
    except Exception:
        return False
    return True


def _ocr_languages() -> str:
    try:  # pragma: no cover - depends on the host machine
        import pytesseract

        available = set(pytesseract.get_languages(config=""))
    except Exception:
        available = set()
    if {"hin", "eng"} <= available:
        return "hin+eng"
    if "eng" in available:
        return "eng"
    return "eng"


def _ocr_image(image: Image.Image) -> str:
    try:
        import pytesseract
    except ImportError as exc:  # pragma: no cover
        raise OCRUnavailable("pytesseract is not installed") from exc
    try:
        return pytesseract.image_to_string(image, lang=_ocr_languages())
    except Exception as exc:  # pragma: no cover - missing language data etc.
        raise ExtractionError(f"OCR failed: {exc}") from exc


def _pdf_text(file_obj) -> tuple[str, int]:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        reader = PdfReader(file_obj)
    except PdfReadError as exc:
        raise ExtractionError("The PDF could not be read (it may be corrupt).") from exc
    pages = len(reader.pages)
    chunks: list[str] = []
    for page in reader.pages:
        try:
            chunks.append(page.extract_text() or "")
        except Exception:  # pragma: no cover - malformed page
            chunks.append("")
    return "\n".join(chunks), pages


def _pdf_ocr(file_obj) -> str:
    """Rasterise a scanned PDF with poppler and OCR the rendered pages."""

    if not shutil.which("pdftoppm"):
        raise OCRUnavailable(
            "This PDF looks scanned. Install Tesseract and Poppler (pdftoppm) to "
            "read it automatically, or type the details manually."
        )
    if not tesseract_available():
        raise OCRUnavailable(
            "This PDF looks scanned and no OCR engine is installed. Type the "
            "details manually — the upload is already saved for you."
        )
    with tempfile.TemporaryDirectory() as tmp:
        stem = os.path.join(tmp, "page")
        try:
            subprocess.run(
                ["pdftoppm", "-r", "200", "-png", file_obj.name, stem],
                check=True,
                capture_output=True,
            )
        except Exception as exc:  # pragma: no cover
            raise ExtractionError(f"Could not rasterise the PDF: {exc}") from exc
        pages = sorted(Path(tmp).glob("page-*.png"))
        texts = []
        for page in pages:
            with Image.open(page) as img:
                texts.append(_ocr_image(img.convert("RGB")))
        return "\n".join(texts)


def extract_upload(upload) -> ExtractionResult:
    """Read text and candidate fields out of an uploaded invitation."""

    name = (getattr(upload, "name", "") or "").lower()
    content = upload.read()
    upload.seek(0)
    if not content:
        raise ExtractionError("The uploaded file is empty.")

    if name.endswith(".pdf") or getattr(upload, "content_type", "") == "application/pdf":
        text, pages = _pdf_text(io.BytesIO(content))
        engine = "pdf-text"
        warnings: list[str] = []
        if len(re.sub(r"\s+", "", text)) < settings.WEDDING_INVITATION_MIN_TEXT_CHARS:
            try:
                ocr_text = _pdf_ocr(io.BytesIO(content))
                if ocr_text.strip():
                    text = ocr_text
                    engine = "pdf-ocr"
                    return parse_invitation(text, engine=engine, warnings=warnings, pages=pages)
                warnings.append(
                    "No readable text was found — the invitation may be a pure "
                    "scan. Please confirm the details manually."
                )
                return parse_invitation(text, engine=engine, warnings=warnings, pages=pages)
            except OCRUnavailable:
                if text.strip():
                    warnings.append(
                        "Little text was extracted from the PDF. Please confirm the "
                        "details manually."
                    )
                    return parse_invitation(text, engine=engine, warnings=warnings, pages=pages)
                raise
        return parse_invitation(text, engine=engine, warnings=warnings, pages=pages)

    # Image upload → OCR
    if not tesseract_available():
        raise OCRUnavailable(
            "Reading a photo needs the Tesseract OCR engine, which is not "
            "installed on this server. The invitation is saved — please type the "
            "details manually."
        )
    try:
        with Image.open(io.BytesIO(content)) as img:
            img = img.convert("RGB")
            text = _ocr_image(img)
    except ExtractionError:
        raise
    except Exception as exc:
        raise ExtractionError("The image could not be read.") from exc
    return parse_invitation(text, engine="ocr", pages=1)


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------
def _clean_name(value: str) -> str:
    value = re.sub(r"\s+", " ", value or "").strip(" .,।:-–—")
    value = re.sub(r"\b(?:weds|wed|&\b.*)$", "", value, flags=re.IGNORECASE).strip()
    return value


def _is_meaningful_name(value: str) -> bool:
    if not value or len(value) < 2:
        return False
    lowered = value.lower().strip()
    if lowered in STOPWORDS:
        return False
    if lowered.startswith(("s/o", "d/o", "w/o", "son of", "daughter of")):
        return False
    letters = [ch for ch in value if ch.isalpha()]
    return len(letters) >= 2


def parse_date(text: str) -> date | None:
    """Find the first plausible date in ``text``."""

    match = re.search(r"\b(\d{4})-(\d{1,2})-(\d{1,2})\b", text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass

    match = re.search(r"\b(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})\b", text)
    if match:
        day, month, year = (int(g) for g in match.groups())
        if 1 <= month <= 12 and 1 <= day <= 31:
            try:
                return date(year, month, day)
            except ValueError:
                pass

    for month_name, month_no in MONTHS_HI.items():
        match = re.search(
            rf"\b(\d{{1,2}})\s*(?:माह\s*)?{re.escape(month_name)}\s*,?\s*(\d{{4}})", text
        )
        if match:
            try:
                return date(int(match.group(2)), month_no, int(match.group(1)))
            except ValueError:
                break

    for month_name, month_no in MONTHS_EN.items():
        match = re.search(
            rf"\b(\d{{1,2}})\s*(?:of\s+)?{month_name}\s*,?\s*(\d{{4}})",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            try:
                return date(int(match.group(2)), month_no, int(match.group(1)))
            except ValueError:
                break
        match = re.search(
            rf"\b{month_name}\s+(\d{{1,2}})\s*,?\s*(\d{{4}})", text, flags=re.IGNORECASE
        )
        if match:
            try:
                return date(int(match.group(2)), month_no, int(match.group(1)))
            except ValueError:
                break
    return None


def parse_time(text: str) -> time | None:
    """Find the first plausible clock time in ``text``."""

    lowered = text.lower()
    meridiem = None
    for word, value in MERIDIEM_HI.items():
        if word in text:
            meridiem = value
            break
    if meridiem is None:
        if "am" in lowered:
            meridiem = "am"
        elif "pm" in lowered:
            meridiem = "pm"

    match = re.search(r"\b(\d{1,2})[:.](\d{2})\s*(a\.?m\.?|p\.?m\.?)?", lowered)
    if match:
        hour, minute = int(match.group(1)), int(match.group(2))
        suffix = (match.group(3) or "").replace(".", "")
        if suffix == "pm" and hour < 12:
            hour += 12
        elif suffix == "am" and hour == 12:
            hour = 0
        elif meridiem == "pm" and hour < 12 and hour >= 1:
            hour += 12
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return time(hour % 24, minute)

    match = re.search(r"(\d{1,2})\s*(?:बजे|बजे\s*का|बजे\s*पर)", text)
    if match:
        hour = int(match.group(1))
        if meridiem == "pm" and hour < 12:
            hour += 12
        if meridiem == "am" and hour == 12:
            hour = 0
        if 0 <= hour <= 23:
            return time(hour, 0)
    return None


def _parse_couple(text: str) -> tuple[str, str]:
    """Best-effort bride/groom detection — returns empty strings when unsure."""

    # Prefer explicit "X weds Y" / "&" patterns with ASCII names first
    patterns = [
        rf"(?P<groom>{_NAME_ASCII})\s*(?:weds|wed|marries|marriage\s+of|&\s*)\s*(?P<bride>{_NAME_ASCII}|{_NAME_DEV})",
        rf"(?P<groom>{_NAME_ASCII}|{_NAME_DEV})\s*(?:weds|wed|marries)\s+(?P<bride>{_NAME_ASCII}|{_NAME_DEV})",
        rf"(?P<bride>{_NAME_ASCII}|{_NAME_DEV})\s*(?:weds|wed|marries)\s+(?P<groom>{_NAME_ASCII}|{_NAME_DEV})",
        rf"(?P<groom>{_NAME_ASCII}|{_NAME_DEV})\s+(?:की|का|के)\s+(?:शादी|विवाह)\s+(?P<bride>{_NAME_ASCII}|{_NAME_DEV})",
        rf"(?P<groom>{_NAME_ASCII}|{_NAME_DEV})\s+(?:साथ|के\s+साथ)\s+(?P<bride>{_NAME_ASCII}|{_NAME_DEV})",
        rf"(?P<groom>{_NAME_ASCII})\s+&\s+(?P<bride>{_NAME_ASCII}|{_NAME_DEV})",
        rf"(?P<groom>{_NAME_DEV})\s+&\s+(?P<bride>{_NAME_ASCII}|{_NAME_DEV})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if not match:
            continue
        groom = _clean_name(match.group("groom"))
        bride = _clean_name(match.group("bride"))
        if _is_meaningful_name(groom) and _is_meaningful_name(bride):
            return groom, bride

    # "S/o X" / "D/o Y" pattern
    father = re.search(
        rf"(?:s/o|s\.\s*o\.)\s*({_NAME_ASCII}|{_NAME_DEV})", text, re.IGNORECASE
    )
    mother = re.search(
        rf"(?:d/o|d\.\s*o\.)\s*({_NAME_ASCII}|{_NAME_DEV})", text, re.IGNORECASE
    )
    if father and mother:
        return _clean_name(father.group(1)), _clean_name(mother.group(1))
    return "", ""


def _parse_venue(text: str) -> tuple[str, str]:
    """Venue name and address, if the invitation states them."""

    venue = ""
    address = ""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    marker = re.compile(
        r"(स्थान|पता|स्थल|venue|venue\s*[:\-]|at\s+)", re.IGNORECASE
    )
    for index, line in enumerate(lines):
        match = marker.search(line)
        if not match:
            continue
        remainder = line[match.end() :].strip(" :-–—")
        remainder = re.sub(r"^(स्थान|पता)\s*[:\-]\s*", "", remainder).strip()
        if remainder and not venue:
            venue = remainder[:200]
            if index + 1 < len(lines):
                address = lines[index + 1][:250]
            break
    if not address:
        for line in lines:
            if re.search(r"(गृह|निवास|मकान|धनी|भवन|house|residence)", line, re.IGNORECASE):
                address = line[:250]
                break
    return venue, address


def _parse_city(text: str) -> tuple[str, str]:
    lowered = text.lower()
    for city, state in CITIES.items():
        if city in lowered:
            display = city.strip()
            return display.title() if display.isascii() else display, state
    return "", ""


def _parse_events(text: str) -> dict[str, dict]:
    """Find the ritual names and their nearby dates/times."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    found: dict[str, dict] = {}
    for index, line in enumerate(lines):
        lowered = line.lower()
        window = " ".join(lines[index : index + 2])
        for latin, english, devanagari in EVENT_KEYWORDS:
            needle = latin.lower()
            if needle not in lowered:
                continue
            key = english
            if key in found:
                break
            event_date = parse_date(window)
            event_time = parse_time(window)
            found[key] = {
                "name": english,
                "name_hi": devanagari,
                "date": event_date.isoformat() if event_date else "",
                "time": event_time.strftime("%H:%M") if event_time else "",
            }
            break
    return found


def _parse_family(text: str) -> list[str]:
    names: list[str] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        lowered = line.lower()
        if any(marker in lowered for marker in FAMILY_MARKERS):
            cleaned = re.sub(r"^[^ऀ-ॿA-Za-z]+", "", line)
            cleaned = re.sub(r"\s{2,}.*$", "", cleaned)
            if len(cleaned) > 2 and cleaned not in names:
                names.append(cleaned[:120])
        if len(names) >= 6:
            break
    return names


def detect_language(text: str) -> str:
    """Guess the invitation language — never claims a dialect we cannot prove."""

    if re.search(r"[ऀ-ॿ]", text):
        if re.search(r"(मैथिली|मैथिलि)", text):
            return "mai"
        if re.search(r"(भोजपुरी|भोजपुरि)", text):
            return "bho"
        return "hi"
    return "en"


def parse_invitation(
    text: str, engine: str = "", warnings: list[str] | None = None, pages: int = 0
) -> ExtractionResult:
    """Turn raw invitation text into candidate wedding fields."""

    warnings = list(warnings or [])
    text = text or ""
    flat = re.sub(r"[ \t]+", " ", text)
    fields: dict[str, dict] = {}

    def add(key: str, value, confidence: float, source: str) -> None:
        if value in (None, "") or key in fields:
            return
        fields[key] = {"value": str(value), "confidence": confidence, "source": source}

    groom, bride = _parse_couple(flat)
    if groom:
        add("groom_name", groom, 0.75, engine)
    if bride:
        add("bride_name", bride, 0.75, engine)

    wedding_date = parse_date(flat)
    if wedding_date:
        add("wedding_date", wedding_date.isoformat(), 0.7, engine)
    ceremony_time = parse_time(flat)
    if ceremony_time:
        add("ceremony_time", ceremony_time.strftime("%H:%M"), 0.6, engine)

    venue, address = _parse_venue(flat)
    if venue:
        add("venue_name", venue, 0.6, engine)
    if address:
        add("venue_address", address, 0.5, engine)

    city, state = _parse_city(flat)
    if city:
        add("venue_city", city, 0.6, engine)
    if state:
        add("venue_state", state, 0.5, engine)

    family = _parse_family(flat)
    if family:
        add("family_names", " · ".join(family), 0.4, engine)

    language = detect_language(flat)
    if flat.strip():
        add("language", language, 0.5, engine)

    events = _parse_events(flat)
    for key, payload in events.items():
        if payload.get("date"):
            add(f"{key.lower()}_date", payload["date"], 0.55, engine)
        if payload.get("time"):
            add(f"{key.lower()}_time", payload["time"], 0.45, engine)
        if payload.get("name"):
            add(f"{key.lower()}_name", payload["name_hi"], 0.6, engine)

    missing = [
        label
        for key, label in (
            ("groom_name", "groom's name"),
            ("bride_name", "bride's name"),
            ("wedding_date", "wedding date"),
            ("venue_name", "venue"),
        )
        if key not in fields
    ]
    if missing:
        warnings.append(
            "Could not read: " + ", ".join(missing) + ". Please fill them in manually."
        )

    return ExtractionResult(
        text=text, fields=fields, engine=engine, warnings=warnings, pages=pages
    )


def build_stored_upload(content: bytes, filename: str) -> ContentFile:
    """Wrap raw bytes in a Django file for storage."""

    return ContentFile(content, name=filename)
