from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from invitations.models import CustomerEvent

User = get_user_model()


def make_event(**kwargs):
    defaults = {
        "bride_name": "प्रिया",
        "groom_name": "अमन",
        "event_title": "अमन व प्रिया",
        "family_head_name": "श्री रामकांत रॉय",
        "native_place": "ग्राम नेहरा, जिला दरभंगा",
        "host_phone": "9876543210",
        "primary_language": "HI",
        "wedding_date": date(2026, 2, 18),
    }
    defaults.update(kwargs)
    return CustomerEvent.objects.create(**defaults)


class DialectFormLabelTests(TestCase):
    """Field names must follow the dialect chosen by the visitor."""

    def setUp(self):
        self.event = make_event()

    def _get(self, url, lang):
        self.client.cookies["dw_lang"] = lang
        return self.client.get(url)

    def test_login_labels_follow_language(self):
        english = self._get(reverse("accounts:login"), "en")
        self.assertContains(english, "Username")
        self.assertContains(english, "Password")
        self.assertNotContains(english, "पासवर्ड")

        hindi = self._get(reverse("accounts:login"), "hi")
        self.assertContains(hindi, "उपयोगकर्ता नाम")
        self.assertContains(hindi, "पासवर्ड")

    def test_signup_labels_follow_language(self):
        english = self._get(reverse("accounts:signup"), "en")
        self.assertContains(english, "Home district")
        self.assertContains(english, "New password")

        hindi = self._get(reverse("accounts:signup"), "hi")
        self.assertContains(hindi, "गृह ज़िला")
        self.assertContains(hindi, "नया पासवर्ड")

        bhojpuri = self._get(reverse("accounts:signup"), "bho")
        self.assertContains(bhojpuri, "यूजर नाम")

    def test_rsvp_labels_follow_language(self):
        url = reverse("invitations:event_detail", args=[self.event.slug])
        english = self._get(url, "en")
        self.assertContains(english, "Family name")
        self.assertContains(english, "Total guests")

        hindi = self._get(url, "hi")
        self.assertContains(hindi, "परिवार का नाम")
        self.assertContains(hindi, "कुल संख्या")

    def test_lead_form_labels_follow_language(self):
        english = self._get(reverse("invitations:home"), "en")
        self.assertContains(english, "District")
        self.assertContains(english, "Event date")

        maithili = self._get(reverse("invitations:home"), "mai")
        self.assertContains(maithili, "जिला")
        self.assertContains(maithili, "शादी के तारीख")

    def test_event_editor_labels_follow_language(self):
        user = User.objects.create_user(
            username="aman", password="secret-pass-123", phone_number="9876543210"
        )
        self.client.force_login(user)
        english = self._get(reverse("invitations:event_create"), "en")
        self.assertContains(english, "Invitation title")
        self.assertContains(english, "Head of the family")

        hindi = self._get(reverse("invitations:event_create"), "hi")
        self.assertContains(hindi, "निमंत्रण शीर्षक")
        self.assertContains(hindi, "परिवार के मुखिया")


class NavigationTests(TestCase):
    """The navbar must be responsive and visible on every screen size."""

    def test_mobile_drawer_markup_is_present(self):
        response = self.client.get(reverse("invitations:home"))
        self.assertContains(response, 'id="dw-mobile-nav"')
        self.assertContains(response, "dw-nav-toggle")
        self.assertContains(response, "dw-langchip")
        self.assertContains(response, "dw-mobilelink")

    def test_navbar_is_sticky_and_uses_compiled_stylesheet(self):
        response = self.client.get(reverse("invitations:home"))
        self.assertContains(response, "sticky top-0")
        self.assertContains(response, "css/app.css")
        self.assertNotContains(response, "cdn.tailwindcss.com")
