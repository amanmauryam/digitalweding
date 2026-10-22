"""Tests for the wedding-website builder.

Covers the whole promised flow: upload → extract → correct → theme →
customise → preview → publish → share, plus the guest facing RSVP and the
privacy rules (drafts are private, other people cannot touch your site).
"""

import io
import time
from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from websites import extraction, services, themes
from websites.models import WeddingEvent, WeddingPhoto, WeddingRSVP, WeddingWebsite

User = get_user_model()


def png_bytes(size=(240, 320), colour=(200, 40, 60)) -> bytes:
    from PIL import Image

    buffer = io.BytesIO()
    Image.new("RGB", size, colour).save(buffer, format="PNG")
    return buffer.getvalue()


def pdf_bytes(text: str = "Aman weds Priya on 18 February 2026 at 7:30 pm") -> bytes:
    """Build a tiny single page PDF with a real text layer."""

    content = f"BT /F1 18 Tf 40 700 Td ({text}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n"
    ).encode()
    return bytes(out)


class WebsiteTestMixin:
    def make_user(self, username="owner", password="secret-pass-123"):
        return User.objects.create_user(
            username=username, password=password, phone_number="9876543210"
        )

    def make_website(self, owner=None, published=False, **kwargs):
        defaults = {
            "owner": owner or self.user,
            "groom_name": "अमन",
            "bride_name": "प्रिया",
            "wedding_date": date(2026, 2, 18),
            "venue_name": "गणेश मंदिर",
            "venue_city": "दरभंगा",
            "language": "hi",
        }
        defaults.update(kwargs)
        website = WeddingWebsite.objects.create(**defaults)
        if published:
            website.publish()
        return website


class UploadFlowTests(WebsiteTestMixin, TestCase):
    """Step 1 — upload the invitation, or start a blank website."""

    def setUp(self):
        self.user = self.make_user()
        self.client.force_login(self.user)

    def test_create_page_is_public(self):
        response = self.client.get(reverse("websites:create"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invitation card")

    def test_dashboard_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse("websites:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_manual_creation_creates_a_draft(self):
        response = self.client.post(reverse("websites:create"), {"manual": "1"})
        website = WeddingWebsite.objects.get(owner=self.user)
        self.assertRedirects(
            response, reverse("websites:review", kwargs={"slug": website.slug})
        )
        self.assertEqual(website.status, WeddingWebsite.STATUS_DRAFT)
        self.assertFalse(website.is_published)

    def test_upload_of_a_text_pdf_extracts_the_details(self):
        upload = SimpleUploadedFile("card.pdf", pdf_bytes(), content_type="application/pdf")
        response = self.client.post(
            reverse("websites:create"), {"invitation": upload, "acknowledgement": "on"}
        )
        website = WeddingWebsite.objects.get(owner=self.user)
        self.assertRedirects(
            response, reverse("websites:review", kwargs={"slug": website.slug})
        )
        self.assertTrue(website.source_invitation)
        self.assertEqual(website.extraction_engine, "pdf-text")
        self.assertEqual(website.groom_name, "Aman")
        self.assertEqual(website.bride_name, "Priya")
        self.assertEqual(website.wedding_date, date(2026, 2, 18))
        self.assertEqual(website.ceremony_time.strftime("%H:%M"), "19:30")
        self.assertTrue(website.needs_review)

    def test_uploaded_invitation_is_kept_outside_the_media_folder(self):
        upload = SimpleUploadedFile("card.pdf", pdf_bytes(), content_type="application/pdf")
        self.client.post(
            reverse("websites:create"), {"invitation": upload, "acknowledgement": "on"}
        )
        website = WeddingWebsite.objects.get(owner=self.user)
        self.assertNotIn("media", website.source_invitation.name.replace("\\", "/"))
        self.assertTrue(website.source_invitation.name.startswith("invitations/"))

    def test_unsupported_file_type_is_rejected(self):
        upload = SimpleUploadedFile(
            "card.exe", b"MZ...", content_type="application/octet-stream"
        )
        response = self.client.post(reverse("websites:create"), {"invitation": upload})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Unsupported file type")
        self.assertEqual(WeddingWebsite.objects.count(), 0)

    def test_empty_file_is_rejected(self):
        upload = SimpleUploadedFile("card.png", b"", content_type="image/png")
        response = self.client.post(reverse("websites:create"), {"invitation": upload})
        self.assertTrue("empty" in response.content.decode().lower() or "खाली" in response.content.decode())

    def test_broken_image_is_rejected(self):
        upload = SimpleUploadedFile("card.png", b"not-an-image", content_type="image/png")
        response = self.client.post(reverse("websites:create"), {"invitation": upload})
        self.assertContains(response, "could not be read")

    def test_image_upload_without_ocr_keeps_the_file_and_offers_manual_entry(self):
        upload = SimpleUploadedFile("card.png", png_bytes(), content_type="image/png")
        response = self.client.post(
            reverse("websites:create"), {"invitation": upload, "acknowledgement": "on"}
        )
        website = WeddingWebsite.objects.get(owner=self.user)
        self.assertRedirects(
            response, reverse("websites:review", kwargs={"slug": website.slug})
        )
        self.assertTrue(website.source_invitation)
        if extraction.tesseract_available():
            self.assertEqual(website.extraction_engine, "ocr")
        else:
            self.assertIn("Tesseract", website.extraction_warnings)


class ReviewAndEditTests(WebsiteTestMixin, TestCase):
    """Steps 2-5 — correct the details, pick a theme, add events and photos."""

    def setUp(self):
        self.user = self.make_user()
        self.client.force_login(self.user)
        self.website = self.make_website()

    def test_review_page_prefills_the_extracted_values(self):
        self.website.extracted_data = {
            "groom_name": {"value": "Aman", "confidence": 0.7, "source": "pdf-text"}
        }
        self.website.save()
        response = self.client.get(
            reverse("websites:review", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Aman")

    def test_saving_the_details_marks_the_extraction_as_confirmed(self):
        self.website.extracted_data = {
            "groom_name": {"value": "Aman", "confidence": 0.7, "source": "pdf-text"}
        }
        self.website.save()
        response = self.client.post(
            reverse("websites:review", kwargs={"slug": self.website.slug}),
            {
                "groom_name": "अमन",
                "bride_name": "प्रिया",
                "wedding_date": "2026-02-18",
                "ceremony_time": "19:30",
                "timezone": "Asia/Kolkata",
                "language": "hi",
            },
        )
        self.assertRedirects(
            response, reverse("websites:themes", kwargs={"slug": self.website.slug})
        )
        self.website.refresh_from_db()
        self.assertFalse(self.website.needs_review)

    def test_theme_change_keeps_every_other_detail(self):
        self.website.venue_name = "गणेश मंदिर"
        self.website.save()
        response = self.client.post(
            reverse("websites:themes", kwargs={"slug": self.website.slug}),
            {"theme": "mithila_heritage"},
        )
        self.assertRedirects(
            response, reverse("websites:customize", kwargs={"slug": self.website.slug})
        )
        self.website.refresh_from_db()
        self.assertEqual(self.website.theme, "mithila_heritage")
        self.assertEqual(self.website.venue_name, "गणेश मंदिर")
        self.assertEqual(self.website.groom_name, "अमन")

    def test_event_can_be_added_and_removed(self):
        url = reverse("websites:events", kwargs={"slug": self.website.slug})
        response = self.client.post(
            url,
            {
                "name": "हल्दी",
                "date": "2026-02-17",
                "start_time": "10:00",
                "end_time": "12:00",
                "venue": "घर",
            },
        )
        self.assertRedirects(response, url)
        event = WeddingEvent.objects.get(website=self.website)
        self.assertEqual(event.name, "हल्दी")

        response = self.client.post(url, {"delete_event": event.pk})
        self.assertRedirects(response, url)
        self.assertEqual(WeddingEvent.objects.count(), 0)

    def test_event_end_time_before_start_time_is_rejected(self):
        response = self.client.post(
            reverse("websites:events", kwargs={"slug": self.website.slug}),
            {"name": "मेहंदी", "start_time": "18:00", "end_time": "10:00"},
        )
        self.assertContains(response, "cannot be before")

    def test_photo_can_be_uploaded_and_removed(self):
        upload = SimpleUploadedFile("photo.png", png_bytes(), content_type="image/png")
        response = self.client.post(
            reverse("websites:photos", kwargs={"slug": self.website.slug}),
            {"image": upload, "caption": "हम दोनों", "kind": "couple"},
        )
        self.assertRedirects(
            response, reverse("websites:photos", kwargs={"slug": self.website.slug})
        )
        photo = WeddingPhoto.objects.get(website=self.website)
        self.assertEqual(photo.caption, "हम दोनों")

        response = self.client.post(
            reverse(
                "websites:photo_delete",
                kwargs={"slug": self.website.slug, "photo_id": photo.pk},
            )
        )
        self.assertRedirects(
            response, reverse("websites:photos", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(WeddingPhoto.objects.count(), 0)

    def test_customisation_saves_toggles_and_rejects_foreign_colours(self):
        url = reverse("websites:customize", kwargs={"slug": self.website.slug})
        response = self.client.post(
            url, {"accent_color": "#d4af37", "show_gallery": "on", "show_story": ""}
        )
        self.assertRedirects(response, reverse("websites:preview", kwargs={"slug": self.website.slug}))
        self.website.refresh_from_db()
        self.assertTrue(self.website.show_gallery)
        self.assertFalse(self.website.show_story)

        response = self.client.post(url, {"accent_color": "#123456"})
        self.assertContains(response, "not part of the theme palette")


class PrivacyTests(WebsiteTestMixin, TestCase):
    """Drafts stay private and nobody may touch somebody else's website."""

    def setUp(self):
        self.user = self.make_user("owner")
        self.other = self.make_user("intruder", password="secret-pass-456")
        self.client.force_login(self.user)
        self.website = self.make_website()

    def test_draft_website_is_not_public(self):
        response = self.client.get(
            reverse("websites:public_site", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_published_website_is_public(self):
        self.website.publish()
        response = self.client.get(
            reverse("websites:public_site", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.website.display_title)

    def test_another_user_cannot_open_the_editor(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse("websites:review", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_another_user_cannot_publish_the_website(self):
        self.client.force_login(self.other)
        response = self.client.post(
            reverse("websites:publish", kwargs={"slug": self.website.slug}),
            {"confirm": "yes"},
        )
        self.assertEqual(response.status_code, 404)
        self.website.refresh_from_db()
        self.assertFalse(self.website.is_published)

    def test_dashboard_only_lists_my_websites(self):
        self.website.publish()
        other_site = self.make_website(
            owner=self.other,
            published=True,
            groom_name="राहुल",
            bride_name="स्नेहा",
        )
        response = self.client.get(reverse("websites:dashboard"))
        self.assertContains(response, self.website.display_title)
        self.assertNotContains(response, other_site.display_title)

    def test_the_original_invitation_is_owner_only(self):
        upload = SimpleUploadedFile("card.pdf", pdf_bytes(), content_type="application/pdf")
        self.client.post(
            reverse("websites:create"), {"invitation": upload, "acknowledgement": "on"}
        )
        website = WeddingWebsite.objects.filter(owner=self.user).order_by('-pk').first()
        response = self.client.get(
            reverse("websites:invitation_source", kwargs={"slug": website.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

        self.client.force_login(self.other)
        response = self.client.get(
            reverse("websites:invitation_source", kwargs={"slug": website.slug})
        )
        self.assertEqual(response.status_code, 404)

    def test_preview_frame_is_not_indexed(self):
        response = self.client.get(
            reverse("websites:preview_frame", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.assertContains(response, 'name="robots" content="noindex, nofollow"')


class PublishAndShareTests(WebsiteTestMixin, TestCase):
    def setUp(self):
        self.user = self.make_user()
        self.client.force_login(self.user)
        self.website = self.make_website()

    def test_publishing_needs_an_explicit_confirmation(self):
        url = reverse("websites:publish", kwargs={"slug": self.website.slug})
        response = self.client.post(url, {})
        self.assertRedirects(response, url)
        self.website.refresh_from_db()
        self.assertFalse(self.website.is_published)

        response = self.client.post(url, {"confirm": "yes"})
        self.assertRedirects(response, reverse("websites:share", kwargs={"slug": self.website.slug}))
        self.website.refresh_from_db()
        self.assertTrue(self.website.is_published)
        self.assertIsNotNone(self.website.published_at)

    def test_publishing_without_a_date_is_refused(self):
        self.website.wedding_date = None
        self.website.save()
        response = self.client.post(
            reverse("websites:publish", kwargs={"slug": self.website.slug}),
            {"confirm": "yes"},
        )
        self.assertRedirects(response, reverse("websites:review", kwargs={"slug": self.website.slug}))
        self.website.refresh_from_db()
        self.assertFalse(self.website.is_published)

    def test_unpublish_takes_the_site_offline_but_keeps_the_link(self):
        self.website.publish()
        response = self.client.post(
            reverse("websites:unpublish", kwargs={"slug": self.website.slug})
        )
        self.assertRedirects(response, reverse("websites:dashboard"))
        self.website.refresh_from_db()
        self.assertFalse(self.website.is_published)
        self.assertEqual(self.website.slug, self.website.slug)

    def test_unpublish_only_accepts_post(self):
        self.website.publish()
        response = self.client.get(
            reverse("websites:unpublish", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(response.status_code, 405)
        self.website.refresh_from_db()
        self.assertTrue(self.website.is_published)

    def test_share_page_offers_a_whatsapp_link(self):
        self.website.publish()
        response = self.client.get(
            reverse("websites:share", kwargs={"slug": self.website.slug})
        )
        self.assertContains(response, "wa.me")
        self.assertContains(response, self.website.public_url())

    def test_whatsapp_url_is_encoded(self):
        url = services.whatsapp_share_url("शादी का निमंत्रण https://example.com/x")
        self.assertTrue(url.startswith("https://wa.me/?text="))
        self.assertNotIn(" ", url)

    def test_csv_export_lists_the_guests(self):
        self.website.publish()
        WeddingRSVP.objects.create(
            website=self.website, guest_name="राम", guest_phone="9876543210"
        )
        response = self.client.get(
            reverse("websites:rsvps_csv", kwargs={"slug": self.website.slug})
        )
        self.assertEqual(response["Content-Type"], "text/csv")
        self.assertIn("9876543210", response.content.decode())

    def test_deleting_the_website_removes_it(self):
        url = reverse("websites:delete", kwargs={"slug": self.website.slug})
        response = self.client.post(url, {"confirm": "yes"})
        self.assertRedirects(response, reverse("websites:dashboard"))
        self.assertEqual(WeddingWebsite.objects.count(), 0)

    def test_the_slug_stays_the_same_when_the_names_change(self):
        original = self.website.slug
        self.website.groom_name = "राहुल"
        self.website.bride_name = "स्नेहा"
        self.website.save()
        self.website.refresh_from_db()
        self.assertEqual(self.website.slug, original)


class PublicRsvpTests(WebsiteTestMixin, TestCase):
    def setUp(self):
        from django.core.cache import cache

        cache.clear()
        self.user = self.make_user()
        self.client.force_login(self.user)
        self.website = self.make_website(published=True)

    def _post(self, **overrides):
        payload = {
            "guest_name": "राम",
            "guest_phone": "9876543210",
            "attending": "True",
            "guest_count": "2",
            "message": "शुभकामनाएँ",
            "started_at": str(time.time() - 30),
        }
        payload.update(overrides)
        return self.client.post(
            reverse("websites:public_rsvp", kwargs={"slug": self.website.slug}), payload
        )

    def test_valid_response_is_stored(self):
        response = self._post()
        self.assertRedirects(
            response, reverse("websites:public_site", kwargs={"slug": self.website.slug})
        )
        rsvp = WeddingRSVP.objects.get(website=self.website)
        self.assertEqual(rsvp.guest_name, "राम")
        self.assertEqual(rsvp.guest_count, 2)
        self.assertTrue(rsvp.attending)

    def test_the_same_phone_number_updates_the_response(self):
        self._post()
        self._post(guest_name="राम कुमार", guest_count="3")
        self.assertEqual(WeddingRSVP.objects.count(), 1)
        rsvp = WeddingRSVP.objects.get(website=self.website)
        self.assertEqual(rsvp.guest_count, 3)

    def test_honeypot_blocks_a_bot(self):
        self._post(company="spam")
        self.assertEqual(WeddingRSVP.objects.count(), 0)

    def test_a_too_fast_submission_is_rejected(self):
        self._post(started_at=str(time.time()))
        self.assertEqual(WeddingRSVP.objects.count(), 0)

    def test_an_invalid_phone_number_is_rejected(self):
        self._post(guest_phone="12345")
        self.assertEqual(WeddingRSVP.objects.count(), 0)

    def test_rsvp_is_closed_when_the_couple_switches_it_off(self):
        self.website.show_rsvp = False
        self.website.save()
        response = self._post()
        self.assertEqual(response.status_code, 404)

    def test_a_draft_website_cannot_receive_responses(self):
        self.website.unpublish()
        response = self._post()
        self.assertEqual(response.status_code, 404)

    def test_rate_limit_stops_a_flood(self):
        from django.core.cache import cache

        cache.clear()
        for _ in range(9):
            self._post()
        self.assertLessEqual(WeddingRSVP.objects.count(), 1)


class ServiceTests(TestCase):
    def test_maps_directions_url_contains_the_venue(self):
        url = services.maps_directions_url("गणेश मंदिर", "गांधी रोड", "दरभंगा")
        self.assertIn("google.com/maps/dir", url)
        self.assertIn("%E0%A4%97", url)  # ग

    def test_every_theme_has_a_template_and_unique_code(self):
        codes = [theme.code for theme in themes.THEMES]
        self.assertEqual(len(codes), len(set(codes)))
        for theme in themes.THEMES:
            self.assertTrue(theme.template.endswith("site.html"))
            self.assertIn("accent", theme.colors)

    def test_get_theme_falls_back_to_the_default(self):
        self.assertEqual(themes.get_theme("does-not-exist").code, themes.DEFAULT_THEME)

    def test_missing_information_lists_what_is_empty(self):
        website = WeddingWebsite(owner=User.objects.create_user(username="x"))
        website.save()
        missing = views_missing(website)
        self.assertIn("Couple names", missing)
        self.assertIn("Wedding date", missing)


def views_missing(website):
    from websites.views import missing_information

    return missing_information(website)


class ExtractionTests(TestCase):
    def test_parse_finds_the_couple_and_the_date(self):
        text = (
            "सादर निमंत्रण\n"
            "Aman weds Priya\n"
            "18 February 2026, 7:30 pm\n"
            "स्थान: गणेश मंदिर, दरभंगा\n"
        )
        result = extraction.parse_invitation(text, engine="test")
        self.assertEqual(result.value("groom_name"), "Aman")
        self.assertEqual(result.value("bride_name"), "Priya")
        self.assertEqual(result.value("wedding_date"), "2026-02-18")
        self.assertEqual(result.value("venue_city"), "दरभंगा")
        self.assertEqual(result.value("venue_state"), "Bihar")
        self.assertFalse(result.warnings)

    def test_date_parsing_handles_devanagari(self):
        self.assertEqual(
            extraction.parse_date("शादी 18 फरवरी 2026 को"), date(2026, 2, 18)
        )

    def test_time_parsing_handles_meridiem(self):
        self.assertEqual(extraction.parse_time("शादी 7:30 pm को").strftime("%H:%M"), "19:30")
        self.assertEqual(extraction.parse_time("शादी सुबह 10 बजे").strftime("%H:%M"), "10:00")

    def test_language_detection(self):
        self.assertEqual(extraction.detect_language("शादी का निमंत्रण"), "hi")
        self.assertEqual(extraction.detect_language("Wedding invitation"), "en")

    def test_empty_text_yields_no_values(self):
        result = extraction.parse_invitation("")
        self.assertEqual(result.fields, {})
        self.assertTrue(result.warnings)

    def test_countdown_math_for_the_hero(self):
        website = WeddingWebsite(
            owner=User.objects.create_user(username="y"),
            wedding_date=date.today() + timedelta(days=10),
        )
        website.save()
        self.assertIsNotNone(website.wedding_date)
