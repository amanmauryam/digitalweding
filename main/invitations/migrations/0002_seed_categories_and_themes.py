"""Seed the default invitation categories and the four Bihari template themes."""

from django.db import migrations

CATEGORIES = [
    ("Biyah (Wedding)", "biyah"),
    ("Chhath Puja", "chhath-puja"),
    ("Griha Pravesh", "griha-pravesh"),
    ("Mundan", "mundan"),
    ("Sangeet", "sangeet"),
    ("Other Sanskar", "other-sanskar"),
]

THEMES = [
    ("MITHILA", "Mithila Madhubani", "madhubani_mithila"),
    ("ROYAL_RAJ", "Royal Rajputana Jamindari", "kohbar_rajputana"),
    ("MODERN_BIHARI", "Modern Minimal Bihari", "modern_bihari_minimal"),
    ("BHOJPURI_FOLK", "Bhojpuri Folk Festival", "bhojpuri_folk_festival"),
]


def seed(apps, schema_editor):
    InvitationCategory = apps.get_model("invitations", "InvitationCategory")
    TemplateTheme = apps.get_model("invitations", "TemplateTheme")

    for name, slug in CATEGORIES:
        InvitationCategory.objects.get_or_create(slug=slug, defaults={"name": name})

    wedding = InvitationCategory.objects.filter(slug="biyah").first()
    if wedding is None:
        return
    for style, title, code in THEMES:
        TemplateTheme.objects.get_or_create(
            template_code=code,
            defaults={"category": wedding, "title": title, "style_type": style},
        )


def unseed(apps, schema_editor):
    InvitationCategory = apps.get_model("invitations", "InvitationCategory")
    TemplateTheme = apps.get_model("invitations", "TemplateTheme")
    TemplateTheme.objects.filter(
        template_code__in=[code for _, _, code in THEMES]
    ).delete()
    InvitationCategory.objects.filter(
        slug__in=[slug for _, slug in CATEGORIES]
    ).delete()


class Migration(migrations.Migration):
    dependencies = [("invitations", "0001_initial")]

    operations = [migrations.RunPython(seed, unseed)]
