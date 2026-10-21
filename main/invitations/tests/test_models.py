from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from invitations.models import (
    CustomerEvent,
    EventFunction,
    GuestBlessing,
    InvitationCategory,
    LeadCapture,
    RSVPResponse,
    TemplateTheme,
)

User = get_user_model()


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


class CustomerEventModelTests(TestCase):
    def test_slug_is_transliterated_and_readable(self):
        event = make_event()
        self.assertEqual(event.slug, "aman-weds-priya-3210")

    def test_slug_is_unique_for_identical_names(self):
        first = make_event()
        second = make_event()
        self.assertNotEqual(first.slug, second.slug)

    def test_explicit_slug_is_kept(self):
        event = make_event(slug="custom-slug")
        self.assertEqual(event.slug, "custom-slug")

    def test_absolute_url(self):
        event = make_event()
        self.assertEqual(event.get_absolute_url(), f"/w/{event.slug}/")

    def test_view_count_increment(self):
        event = make_event()
        event.increment_views()
        event.refresh_from_db()
        self.assertEqual(event.view_count, 1)

    def test_rsvp_aggregates(self):
        event = make_event()
        RSVPResponse.objects.create(
            event=event,
            guest_name="राम",
            guest_phone="9876500001",
            attending_status="YES",
            guest_count=3,
        )
        RSVPResponse.objects.create(
            event=event,
            guest_name="श्याम",
            guest_phone="9876500002",
            attending_status="NO",
        )
        self.assertEqual(event.total_rsvps, 2)
        self.assertEqual(event.attending_count, 3)


class EventFunctionModelTests(TestCase):
    def setUp(self):
        self.event = make_event()

    def test_function_meta_uses_bihari_schema(self):
        function = EventFunction.objects.create(
            event=self.event,
            function_code="MATKOR",
            function_name="माटकोर",
            date_and_time=timezone.now() + timedelta(days=1),
            venue_name="माटकोर भूमि",
            address="ग्राम नेहरा",
        )
        self.assertEqual(function.devanagari_name, "माटकोर")
        self.assertEqual(function.folk_music, "Matkor Folk Songs")
        self.assertEqual(function.accent_color, "#9A3412")

    def test_functions_are_ordered_by_time(self):
        base = timezone.now()
        EventFunction.objects.create(
            event=self.event,
            function_code="HALDI",
            function_name="हल्दी",
            date_and_time=base + timedelta(days=2),
            venue_name="आम बाग",
            address="पटना",
        )
        EventFunction.objects.create(
            event=self.event,
            function_code="TILAK",
            function_name="तिलक",
            date_and_time=base,
            venue_name="निवास",
            address="दरभंगा",
        )
        names = [f.function_code for f in self.event.functions_in_order()]
        self.assertEqual(names, ["TILAK", "HALDI"])


class TemplateThemeModelTests(TestCase):
    def test_theme_exposes_palette_preset(self):
        category, _ = InvitationCategory.objects.get_or_create(
            slug="biyah", defaults={"name": "Biyah"}
        )
        theme = TemplateTheme.objects.create(
            category=category,
            title="Royal Rajputana",
            template_code="kohbar_rajputana",
            style_type="ROYAL_RAJ",
        )
        self.assertEqual(theme.accent_color, "#800020")
        self.assertIn("primary", theme.preset)


class SeededDefaultsTests(TestCase):
    def test_categories_and_themes_are_seeded(self):
        self.assertTrue(InvitationCategory.objects.filter(slug="biyah").exists())
        self.assertEqual(TemplateTheme.objects.count(), 4)
        self.assertTrue(
            TemplateTheme.objects.filter(template_code="kohbar_rajputana").exists()
        )


class LeadAndBlessingTests(TestCase):
    def test_lead_is_created(self):
        lead = LeadCapture.objects.create(phone_number="9876543210", district="Patna")
        self.assertIn("9876543210", str(lead))

    def test_blessing_defaults_to_paan(self):
        event = make_event()
        blessing = GuestBlessing.objects.create(event=event, guest_name="सीता")
        self.assertEqual(blessing.kind, "PAAN")
        self.assertEqual(event.blessing_count, 1)
