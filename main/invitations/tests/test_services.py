from datetime import date

from django.test import TestCase

from invitations import bihari, i18n, services
from invitations.models import CustomerEvent, EventFunction, TemplateTheme, InvitationCategory
from invitations.transliterate import transliterate


def make_event(**kwargs):
    defaults = {
        "bride_name": "प्रिया",
        "groom_name": "अमन",
        "event_title": "अमन व प्रिया",
        "family_head_name": "श्री रामकांत रॉय",
        "native_place": "ग्राम: नेहरा, जिला: दरभंगा",
        "host_phone": "9876543210",
        "primary_language": "HI",
        "wedding_date": date(2026, 2, 18),
    }
    defaults.update(kwargs)
    return CustomerEvent.objects.create(**defaults)


class TransliterationTests(TestCase):
    def test_common_names(self):
        self.assertEqual(transliterate("अमन"), "aman")
        self.assertEqual(transliterate("प्रिया"), "priya")
        self.assertEqual(transliterate("सुनीता"), "sunita")
        self.assertEqual(transliterate("राहुल"), "rahul")

    def test_full_name_with_prefix(self):
        self.assertEqual(transliterate("श्री रामकांत रॉय"), "shri ramakant roy")

    def test_empty_input(self):
        self.assertEqual(transliterate(""), "")


class WhatsAppMessageTests(TestCase):
    def setUp(self):
        self.event = make_event()

    def test_hindi_template_contains_respectful_tone(self):
        message = services.build_whatsapp_message(self.event)
        self.assertIn("सहर्ष निमंत्रण", message)
        self.assertIn("दर्शनाभिलाषी", message)
        self.assertIn("रॉय", message)
        self.assertIn(self.event.share_url if hasattr(self.event, "share_url") else "/w/", message)

    def test_maithili_template(self):
        event = make_event(primary_language="MAI")
        message = services.build_whatsapp_message(event)
        self.assertIn("सहर्ष निमंत्रण", message)
        self.assertNotIn("आपकी उपस्थिति", message)

    def test_english_template(self):
        event = make_event(primary_language="EN")
        message = services.build_whatsapp_message(event)
        self.assertIn("cordially invite", message)

    def test_guest_tag_is_appended_to_link(self):
        message = services.build_whatsapp_message(self.event, "शर्मा परिवार")
        self.assertIn("guest=", message)

    def test_function_names_are_listed(self):
        EventFunction.objects.create(
            event=self.event,
            function_code="TILAK",
            function_name="तिलकोत्सव",
            date_and_time="2026-02-16T09:30",
            venue_name="निवास",
            address="ग्राम नेहरा",
        )
        message = services.build_whatsapp_message(self.event)
        self.assertIn("तिलकोत्सव", message)

    def test_whatsapp_link_is_built(self):
        link = services.whatsapp_link("नमस्ते")
        self.assertTrue(link.startswith("https://wa.me/?text="))

    def test_whatsapp_link_with_phone(self):
        link = services.whatsapp_link("नमस्ते", "+91 98765 43210")
        self.assertTrue(link.startswith("https://wa.me/919876543210?text="))

    def test_share_url_is_absolute(self):
        url = services.event_share_url(self.event)
        self.assertTrue(url.startswith("http"))
        self.assertIn(self.event.slug, url)


class BihariSchemaTests(TestCase):
    def test_seven_rituals_are_defined(self):
        self.assertEqual(
            list(bihari.FUNCTION_TEMPLATES.keys()),
            [
                "TILAK",
                "MATKOR",
                "HALDI",
                "PARICHAWAN",
                "JAIMALA",
                "KOHBAR",
                "RECEPTION",
            ],
        )

    def test_palette_matches_design_spec(self):
        self.assertEqual(bihari.PALETTE["sindoor"], "#800020")
        self.assertEqual(bihari.PALETTE["genda"], "#EAB308")
        self.assertEqual(bihari.PALETTE["ochre"], "#C5A059")
        self.assertEqual(bihari.PALETTE["teal"], "#0D9488")
        self.assertEqual(bihari.PALETTE["terracotta"], "#9A3412")

    def test_every_ritual_has_folk_music_and_blurb(self):
        for code, data in bihari.FUNCTION_TEMPLATES.items():
            self.assertTrue(data["folk_music"], code)
            self.assertTrue(data["accent"].startswith("#"), code)
            for lang in ("hi", "mai", "bho", "en"):
                self.assertTrue(data["blurb"].get(lang), f"{code}/{lang}")


class DialectTests(TestCase):
    def test_all_keys_have_four_dialects(self):
        for key, entry in i18n.STRINGS.items():
            for lang in ("hi", "mai", "bho", "en"):
                self.assertIn(lang, entry, f"{key}/{lang}")

    def test_language_normalisation(self):
        self.assertEqual(i18n.normalise("HI"), "hi")
        self.assertEqual(i18n.normalise("mai"), "mai")
        self.assertEqual(i18n.normalise("unknown"), "hi")

    def test_translation_fallback(self):
        self.assertEqual(i18n.get_string("nav_home", "en"), "Home")
        self.assertEqual(i18n.get_string("missing_key", "en"), "missing_key")

    def test_language_meta_exposes_native_labels(self):
        labels = {item["code"]: item["label"] for item in i18n.LANG_META}
        self.assertEqual(labels["hi"], "हिन्दी")
        self.assertEqual(labels["mai"], "मैथिली")
        self.assertEqual(labels["bho"], "भोजपुरी")


class ThemePresetTests(TestCase):
    def test_preset_contains_palette_tokens(self):
        event = make_event()
        tokens = services.template_preview_seed(event)
        self.assertEqual(tokens["primary"], "#800020")
        self.assertIn("sindoor", tokens)
