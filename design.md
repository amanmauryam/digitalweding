🏛️ DigitalWedding Architecture & Design Specification (design.md)
Project Name: DigitalWedding (digitalwedding.in / digitalwedding.com)
Tagline: "Bihar Ke Parampara Aur Aadhunikta Ka Sunder Milap"
Core Stack: Python 3.12, Django 5.x, PostgreSQL, Tailwind CSS, Alpine.js / HTMX
Target Market: Patna, Muzaffarpur, Gaya, Bhagalpur, Darbhanga + Bihari Diaspora Across Delhi, Bengaluru, Mumbai & Gulf/NRI
Business Model (Phase 1): Free Live Customizer, Direct WhatsApp Shareability, Lead Capture & High-Conversion Experience (No Payment Gateway Logic).

1. Executive Summary & Product Vision
DigitalWedding is built specifically to bridge the rich cultural traditions of Bihar (Mithila, Bhojpuri, Magahi heritage) with modern digital convenience. Instead of generic Westernized templates, it offers a deeply rooted Bihari experience where weddings are treated as community festivals (Biyah).
Core Value Proposition
"Ghar Baithe Ek Click Mein Bhejein Sneh Nimantran — Sabhi Sanskar, Lok Geet Aur Google Maps Ke Saath."
Key Bihari Cultural Integration Anchors
Traditional Function Framework: Pre-built flows for Bihari wedding rituals (Tilak, Matkor, Haldi/Ubtan, Cheka, Parichhawan, Dwar Puja, Jaimala, Kohbar Ghar, Bidaai).
Authentic Bihari Folk Soundscapes: Optional background tracks featuring Shehnai, Sohar, Vivah Geet, and classical Flute compositions.
Mithila / Kohbar Art Visual Themes: Handcrafted Madhubani borders featuring auspicious symbols like Lotus (Kamal), Peacock (Mor), Bamboo (Bans), Fish (Machhali), and Kalash.
Devanagari & Regional Dialects: Native typography support for Hindi, Maithili, Bhojpuri, and Magahi, ensuring honorific terms like "Sneh Nimantran", "Aapka Saadar Aahwan", and "Gramin Bhasha" are displayed perfectly.

2. Bihar-Centric UI/UX & Design System
🎨 Bihari Cultural Color Palette
Sindoor Red / Crimson (#800020 / #B22222): Primary bridal and ritual shade symbolizing Suhag and auspiciousness.
Genda Phool Yellow / Haldi Gold (#EAB308 / #D4AF37): Represents Matkor, Ubtan, and Haldi ceremonies.
Mithila Silk Ochre (#C5A059): Traditional parchment tone used for Madhubani-inspired card backgrounds.
Peacock Teal (#0D9488 / #064E3B): Represents the Kohbar Ghar fertility motifs and Mehendi functions.
Ganga Clay Terracotta (#9A3412): Earthy tone for Matkor (sacred clay digging ritual) cards.
✒️ Devanagari & Bihari Font Stack
Primary Devanagari Heading: Rozha One, Yatra One (Classic royal headline fonts for shlokas & groom/bride names)
Subhead & Body: Tiro Devanagari Hindi, Noto Sans Devanagari
English Luxury Headers: Playfair Display, Cinzel
🎭 Unique Bihari Micro-Interactions
Virtual "Laddoo / Paan" Greeting Badge: An option on the guest side to tap a virtual Paan-Laddoo icon to send blessings.
Interactive Kohbar Door Opening: Instead of a simple wax seal, guests tap an intricate Kohbar Ghar painted door that unlocks with a soft Shehnai sound effect.
One-Tap Dialect Switcher: Instant top bar toggle: [ Hindi ] | [ Maithili ] | [ Bhojpuri ] | [ English ].

3. Bihari Function & Ritual Schema Mapping
To make the platform feel 100% authentic to families in Bihar, the system defaults to traditional Bihari function templates:
Function Code
Bihari Name
Display Accent Color
Associated Folk Music
TILAK
Tilakotsav (तिलकोत्सव)
Royal Crimson
Mangal Dhwani
MATKOR
Matkor & Sacred Clay Rite (माटकोर)
Clay Terracotta
Matkor Folk Songs
HALDI
Haldi-Ubtan & Imli Ghotai (हल्दी-उबटन)
Genda Yellow
Vivah Haldi Geet
PARICHAWAN
Dwar Puja & Parichhawan (द्वार पूजा)
Vermillion Red
Shehnai & Nagada
JAIMALA
Jaimala & Subh Vivah (जयमाला व शुभ विवाह)
Royal Gold
Vedic Shloka
KOHBAR
Kohbar Pujan (कोहबर पूजन)
Peacock Green
Kohbar Folk Geet
RECEPTION
Preeti Bhoj / Samdhan Bhent (प्रीतिभोज)
Imperial Blue
Light Classical Flute



4. Technical Architecture & Django Implementation
A. Database Schema (models.py)
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

class User(AbstractUser):
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    home_district = models.CharField(max_length=100, default='Patna', help_text="e.g., Patna, Darbhanga, Gaya, Bhojpur")

class InvitationCategory(models.Model):
    name = models.CharField(max_length=100) # e.g., Biyah (Wedding), Chhath Puja, Griha Pravesh, Mundan
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name

class TemplateTheme(models.Model):
    THEME_STYLES = [
        ('MITHILA', 'Mithila & Madhubani Art Style'),
        ('ROYAL_RAJ', 'Royal Rajputana / Jamindari Theme'),
        ('MODERN_BIHARI', 'Modern Minimalist Bihari Accent'),
        ('BHOJPURI_FOLK', 'Bhojpuri Cultural Aesthetic'),
    ]

    category = models.ForeignKey(InvitationCategory, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    template_code = models.CharField(max_length=100) # e.g., 'kohbar_rajputana'
    style_type = models.CharField(max_length=20, choices=THEME_STYLES, default='MITHILA')
    preview_image = models.ImageField(upload_to='templates/previews/')
    default_audio_url = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.get_style_type_display()})"

class CustomerEvent(models.Model):
    LANG_CHOICES = [
        ('HI', 'Hindi'),
        ('MAI', 'Maithili'),
        ('BHO', 'Bhojpuri'),
        ('EN', 'English'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    template = models.ForeignKey(TemplateTheme, on_delete=models.SET_NULL, null=True)
    
    # Event Info
    bride_name = models.CharField(max_length=100)
    groom_name = models.CharField(max_length=100)
    event_title = models.CharField(max_length=200, help_text="e.g., Aman weds Priya")
    slug = models.SlugField(unique=True)
    
    # Bihari Host Context
    family_head_name = models.CharField(max_length=150, help_text="e.g., Shri Ramakant Roy")
    native_place = models.CharField(max_length=150, blank=True, null=True, help_text="e.g., Gram: Nehra, Jila: Darbhanga")
    host_phone = models.CharField(max_length=15)
    
    primary_language = models.CharField(max_length=5, choices=LANG_CHOICES, default='HI')
    wedding_date = models.DateField()
    custom_shloka = models.TextField(default="वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ। निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा॥")
    welcome_message = models.TextField(default="परम पिता परमेश्वर की असीम अनुकंपा से हमारे सुपुत्र/सुपुत्री के शुभ विवाह अवसर पर आपका हार्दिक अभिनंदन है।")
    
    # Analytics
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(default=True)
    view_count = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.groom_name}-weds-{self.bride_name}-{self.host_phone[-4:]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.event_title

class EventFunction(models.Model):
    event = models.ForeignKey(CustomerEvent, related_name='functions', on_delete=models.CASCADE)
    function_name = models.CharField(max_length=100) # Tilak, Matkor, Haldi, Dwar Puja, Jaimala, Preeti Bhoj
    date_and_time = models.DateTimeField()
    venue_name = models.CharField(max_length=200, help_text="e.g., Maurya Hotel, Patna / Village Residence")
    address = models.TextField()
    google_maps_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return f"{self.function_name} - {self.event.event_title}"

class RSVPResponse(models.Model):
    event = models.ForeignKey(CustomerEvent, related_name='rsvps', on_delete=models.CASCADE)
    guest_name = models.CharField(max_length=150)
    guest_phone = models.CharField(max_length=15)
    guest_family_tag = models.CharField(max_length=150, blank=True, null=True, help_text="e.g., Verma Parivar")
    attending_status = models.CharField(max_length=20, choices=[('YES', 'Aayenge (Aastha/Aadhar)'), ('NO', 'Sneh Sahit Kshama')])
    guest_count = models.PositiveIntegerField(default=1)
    blessing_message = models.TextField(blank=True, null=True, help_text="Subhkaamnaayein for Bride & Groom")
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.guest_name} - {self.attending_status}"


5. Bihari Conversion Strategy & Growth Plan
A. Pre-built Bihari WhatsApp Invitation Messages
In the user dashboard, generate pre-written WhatsApp templates reflecting respectful Bihari tone:
Formal Hindi/Maithili WhatsApp Template: "ॐ श्री गणेशाय नमः ॥ स्नेही आत्मीय जन, श्री रामकांत रॉय (ग्राम- नेहरा, दरभंगा) के परिवार की तरफ से सहर्ष निमंत्रण। हमारे चि० अमन संग आ०प्र० प्रिया के विवाह उत्सव ("विवाह बंधन") में आपकी उपस्थिति सादर प्रार्थनीय है।
वेन्यू लोकेशन, माटकोर, हल्दी एवं प्रीतिभोज का पूरा विवरण देखने के लिए नीचे दिए लिंक पर क्लिक करें: https://digitalwedding.in/w/aman-weds-priya?guest=Sharma+Parivar
दर्शनाभिलाषी: समस्त रॉय परिवार"
B. High Performance on Low 4G Mobile Networks
Since many wedding guests in regional towns access the site over variable 4G networks:
SVG Madhubani Vectors: High-resolution icons rendered in inline compressed SVG for instantly sharp, ultra-light graphics.
WebP Compression: All image assets kept under 80KB.
Instant Interactive Fallback: Background music pauses by default until user taps screen to prevent audio stalling.
