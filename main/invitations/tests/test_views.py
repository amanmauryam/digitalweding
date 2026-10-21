from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from invitations.models import CustomerEvent, GuestBlessing, LeadCapture, RSVPResponse

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


class PublicPageTests(TestCase):
    def setUp(self):
        self.event = make_event()

    def test_home_renders(self):
        response = self.client.get(reverse("invitations:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "DigitalWedding")

    def test_event_detail_renders_and_counts_views(self):
        url = reverse("invitations:event_detail", args=[self.event.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.event.groom_name)
        self.event.refresh_from_db()
        self.assertEqual(self.event.view_count, 1)

    def test_unpublished_event_is_hidden(self):
        event = make_event(is_published=False)
        response = self.client.get(reverse("invitations:event_detail", args=[event.slug]))
        self.assertEqual(response.status_code, 404)

    def test_guest_tag_is_prefilled(self):
        url = reverse("invitations:event_detail", args=[self.event.slug])
        response = self.client.get(url, {"guest": "शर्मा परिवार"})
        self.assertContains(response, "शर्मा परिवार")

    def test_api_functions_endpoint(self):
        url = reverse("invitations:api_functions", args=[self.event.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["functions"], [])


class RsvpTests(TestCase):
    def setUp(self):
        self.event = make_event()
        self.url = reverse("invitations:rsvp_create", args=[self.event.slug])

    def test_rsvp_is_saved(self):
        response = self.client.post(
            self.url,
            {
                "guest_name": "रामकांत सिंह",
                "guest_phone": "9876543210",
                "guest_family_tag": "सिंह परिवार",
                "attending_status": "YES",
                "guest_count": 2,
                "blessing_message": "शुभकामनाएँ",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(RSVPResponse.objects.count(), 1)
        rsvp = RSVPResponse.objects.get()
        self.assertEqual(rsvp.guest_count, 2)
        self.assertTrue(rsvp.is_attending)

    def test_invalid_phone_is_rejected(self):
        response = self.client.post(
            self.url,
            {
                "guest_name": "राम",
                "guest_phone": "12345",
                "attending_status": "YES",
                "guest_count": 1,
            },
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(RSVPResponse.objects.count(), 0)

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)


class BlessingTests(TestCase):
    def test_blessing_is_saved(self):
        event = make_event()
        url = reverse("invitations:bless_create", args=[event.slug])
        response = self.client.post(
            url, {"guest_name": "सीता", "kind": "LADDOO", "message": "शुभ विवाह"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(GuestBlessing.objects.count(), 1)


class LeadCaptureTests(TestCase):
    def test_lead_is_saved(self):
        response = self.client.post(
            reverse("invitations:lead_create"),
            {"phone_number": "9876543210", "name": "रमा", "district": "Patna"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(LeadCapture.objects.count(), 1)


class LanguageSwitchTests(TestCase):
    def test_dialect_can_be_switched(self):
        response = self.client.get(reverse("invitations:home"), {"lang": "mai"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "मुख्य पन्ना")
        self.assertIn("dw_lang", response.cookies)

    def test_language_endpoint_sets_cookie_and_redirects(self):
        response = self.client.post(
            reverse("invitations:set_language"),
            {"lang": "bho", "next": "/"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.cookies["dw_lang"].value, "bho")


class DashboardTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="aman", password="secret-pass-123", phone_number="9876543210"
        )
        self.other = User.objects.create_user(username="other", password="secret-pass-123")
        self.event = make_event(user=self.user)

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("invitations:dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_lists_own_events(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("invitations:dashboard"))
        self.assertContains(response, self.event.event_title)

    def test_cannot_edit_event_of_another_user(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("invitations:event_edit", args=[self.event.slug]))
        self.assertEqual(response.status_code, 404)

    def test_event_can_be_created(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("invitations:event_create"),
            {
                "bride_name": "नेहा",
                "groom_name": "राहुल",
                "event_title": "राहुल व नेहा",
                "family_head_name": "श्री किशोर सिंह",
                "host_phone": "9876500000",
                "primary_language": "MAI",
                "wedding_date": "2026-03-01",
                "custom_shloka": "श्लोक",
                "welcome_message": "सादर आह्वान",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = CustomerEvent.objects.get(event_title="राहुल व नेहा")
        self.assertEqual(created.user, self.user)
        self.assertEqual(created.slug, "rahul-weds-neha-0000")

    def test_function_can_be_added_and_removed(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("invitations:event_functions", args=[self.event.slug]),
            {
                "function_code": "TILAK",
                "function_name": "तिलकोत्सव",
                "date_and_time": "2026-02-16T09:30",
                "venue_name": "निवास",
                "address": "ग्राम नेहरा",
            },
        )
        self.assertEqual(response.status_code, 302)
        function = self.event.functions.get()
        self.assertEqual(function.function_name, "तिलकोत्सव")

        response = self.client.post(
            reverse(
                "invitations:function_delete", args=[self.event.slug, function.pk]
            )
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.event.functions.count(), 0)

    def test_share_page_contains_whatsapp_message(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("invitations:event_share", args=[self.event.slug]))
        self.assertContains(response, "सहर्ष निमंत्रण")
        self.assertContains(response, "wa.me")

    def test_event_form_has_live_customizer_preview(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("invitations:event_create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "dwCustomizer")
        self.assertContains(response, "DW_THEME_PALETTE")
        self.assertContains(response, "लाइव प्रीव्यू")

    def test_event_form_exposes_theme_palette(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("invitations:event_create"))
        palette = response.context["theme_palette"]
        self.assertTrue(palette)
        for preset in palette.values():
            self.assertIn("primary", preset)


class AccountTests(TestCase):
    def test_signup_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse("accounts:signup"),
            {
                "username": "priya",
                "password1": "sup3r-secret-pass",
                "password2": "sup3r-secret-pass",
                "first_name": "प्रिया",
                "last_name": "रॉय",
                "email": "priya@example.com",
                "phone_number": "9876543210",
                "home_district": "Darbhanga",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="priya").exists())

    def test_login_page_renders(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertEqual(response.status_code, 200)
