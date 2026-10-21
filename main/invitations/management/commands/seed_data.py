"""Seed the Bihari function schema, invitation themes and a demo invitation.

Usage::

    python manage.py seed_data
    python manage.py seed_data --demo   # also create a demo invitation
"""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from invitations import bihari
from invitations.models import (
    CustomerEvent,
    EventFunction,
    InvitationCategory,
    TemplateTheme,
)

THEME_SEEDS = [
    ("MITHILA", "Mithila Madhubani", "madhubani_mithila"),
    ("ROYAL_RAJ", "Royal Rajputana Jamindari", "kohbar_rajputana"),
    ("MODERN_BIHARI", "Modern Minimal Bihari", "modern_bihari_minimal"),
    ("BHOJPURI_FOLK", "Bhojpuri Folk Festival", "bhojpuri_folk_festival"),
]


class Command(BaseCommand):
    help = "Seed categories, themes and (optionally) a demo invitation."

    def add_arguments(self, parser):
        parser.add_argument(
            "--demo",
            action="store_true",
            help="Also create a demo invitation with all seven Bihari rituals.",
        )

    def handle(self, *args, **options):
        categories = {}
        for name, slug in bihari.DEFAULT_CATEGORIES:
            category, _ = InvitationCategory.objects.get_or_create(
                slug=slug, defaults={"name": name}
            )
            categories[slug] = category
            self.stdout.write(f"category: {category}")

        wedding = categories.get("biyah")
        for style, title, code in THEME_SEEDS:
            theme, created = TemplateTheme.objects.get_or_create(
                template_code=code,
                defaults={
                    "category": wedding,
                    "title": title,
                    "style_type": style,
                },
            )
            self.stdout.write(
                f"{'created' if created else 'exists'}: theme {theme.title} ({style})"
            )

        if options["demo"]:
            self._create_demo(wedding)

    def _create_demo(self, category):
        if CustomerEvent.objects.filter(
            groom_name="अमन", bride_name="प्रिया"
        ).exists():
            self.stdout.write("demo invitation already exists")
            return

        user, _ = User.objects.get_or_create(
            username="demo",
            defaults={"first_name": "Aman", "last_name": "Kumar", "phone_number": "9876543210"},
        )
        theme = TemplateTheme.objects.filter(template_code="kohbar_rajputana").first()
        event = CustomerEvent.objects.create(
            user=user,
            template=theme,
            bride_name="प्रिया",
            groom_name="अमन",
            event_title="अमन व प्रिया",
            family_head_name="श्री रामकांत रॉय",
            native_place="ग्राम: नेहरा, जिला: दरभंगा",
            host_phone="9876543210",
            primary_language="HI",
            wedding_date=(timezone.now() + timedelta(days=45)).date(),
        )

        venues = [
            ("TILAK", "माटकोर एवं शुभ गंगा स्नान", "श्री रामकांत रॉय निवास, ग्राम नेहरा"),
            ("MATKOR", "माटकोर समारोह", "माटकोर भूमि, ग्राम नेहरा"),
            ("HALDI", "हल्दी-उबटन", "आम बाग, मौर्या होटल, पटना"),
            ("PARICHAWAN", "द्वार पूजा एवं प्रीतिभोज", "सभा मंडप, गांधा मैदान, दरभंगा"),
            ("JAIMALA", "जयमाला एवं शुभ विवाह", "मौर्या होटल, पटना"),
            ("KOHBAR", "कोहबर पूजन", "नव नवजोक, कोहबर घर, दरभंगा"),
            ("RECEPTION", "प्रीतिभोज (सम्धान भेण्ट)", "गोलमेज, पटना"),
        ]
        base = timezone.now() + timedelta(days=44)
        for index, (code, name, venue) in enumerate(venues):
            EventFunction.objects.create(
                event=event,
                function_code=code,
                function_name=name,
                date_and_time=base + timedelta(days=index * 3, hours=8),
                venue_name=venue,
                address=f"{venue}, बिहार",
                google_maps_url=None,
            )

        self.stdout.write(f"demo invitation: {event.get_absolute_url()}")
