"""Gramin Bhasha — dialect layer for the UI.

The platform ships four interface languages (design.md §2): Hindi, Maithili,
Bhojpuri and English.  Translations live in-process as plain dictionaries so
the switcher works instantly on low-bandwidth 4G connections without pulling
down a gettext catalogue.

Language codes are ISO-639-1 (``hi``/``mai``/``bho``/``en``); the database
stores the upper-case legacy codes ``HI``/``MAI``/``BHO``/``EN``.
"""

from __future__ import annotations

from django.forms import Textarea, TextInput
from django.http import HttpRequest

DEFAULT_LANG = "hi"

LANG_META = [
    {"code": "hi", "legacy": "HI", "label": "हिन्दी", "english": "Hindi"},
    {"code": "mai", "legacy": "MAI", "label": "मैथिली", "english": "Maithili"},
    {"code": "bho", "legacy": "BHO", "label": "भोजपुरी", "english": "Bhojpuri"},
    {"code": "en", "legacy": "EN", "label": "English", "english": "English"},
]

LEGACY_TO_CODE = {item["legacy"]: item["code"] for item in LANG_META}
CODE_TO_LEGACY = {item["code"]: item["legacy"] for item in LANG_META}

LANG_COOKIE = "dw_lang"


STRINGS: dict[str, dict[str, str]] = {
    # --- Navigation -------------------------------------------------------
    "nav_home": {
        "hi": "होम",
        "mai": "मुख्य पन्ना",
        "bho": "मुख्य पन्ना",
        "en": "Home",
    },
    "nav_my_events": {
        "hi": "मेरे कार्यक्रम",
        "mai": "हमर कार्यक्रम",
        "bho": "हमर कार्यक्रम",
        "en": "My Events",
    },
    "nav_new_invitation": {
        "hi": "नया निमंत्रण बनाएँ",
        "mai": "नव निमंत्रण बनाउ",
        "bho": "नया निमंत्रण बनाई",
        "en": "Create Invitation",
    },
    "nav_login": {
        "hi": "लॉगिन",
        "mai": "लगइन",
        "bho": "लगइन",
        "en": "Login",
    },
    "nav_logout": {
        "hi": "लॉग आउट",
        "mai": "लग आउट",
        "bho": "लग आउट",
        "en": "Logout",
    },
    "nav_signup": {
        "hi": "खाता बनाएँ",
        "mai": "खाता बनाउ",
        "bho": "खाता बनाई",
        "en": "Sign up",
    },
    "nav_menu": {
        "hi": "मेन्यू",
        "mai": "मेनु",
        "bho": "मेन्यू",
        "en": "Menu",
    },
    "nav_open_menu": {
        "hi": "मेन्यू खोलें",
        "mai": "मेनु खोलीं",
        "bho": "मेन्यू खोलीं",
        "en": "Open menu",
    },
    "nav_close_menu": {
        "hi": "मेन्यू बंद करें",
        "mai": "मेनु बन्द करीं",
        "bho": "मेन्यू बंद करीं",
        "en": "Close menu",
    },
    # --- Landing page -----------------------------------------------------
    "hero_kicker": {
        "hi": "बिहार की परंपरा और आधुनिकता का सुंदर मिलन",
        "mai": "बिहार के परंपरा आ आधुनिकता के सुंदर मिलन",
        "bho": "बिहार के परंपरा आ आधुनिकता के सुंदर मिलन",
        "en": "Where Bihar's heritage meets modern convenience",
    },
    "hero_title": {
        "hi": "घर बैठे एक क्लिक में भेजें स्नेह निमंत्रण",
        "mai": "घर बैठि एक क्लिक में भेजी स्नेह निमंत्रण",
        "bho": "घर बैठे एक क्लिक में भेजी स्नेह निमंत्रण",
        "en": "Send heartfelt invitations with a single tap, from home",
    },
    "hero_subtitle": {
        "hi": "सभी संस्कार, लोक गीत और गूगल मैप्स के साथ — मधुबनी के रंगों में।",
        "mai": "सभी संस्कार, लोक गीत आ गूगल मैप्स के साथ — मधुबनी के रंग में।",
        "bho": "सभी संस्कार, लोक गीत आ गूगल मैप्स के साथ — मधुबनी के रंग में।",
        "en": "Every ritual, folk song and Google Map — painted in Madhubani colour.",
    },
    "hero_cta_primary": {
        "hi": "मुफ़्त निमंत्रण बनाएँ",
        "mai": "मुफ़्त निमंत्रण बनाउ",
        "bho": "मुफ़्त निमंत्रण बनाई",
        "en": "Create a free invitation",
    },
    "hero_cta_secondary": {
        "hi": "नमूना देखें",
        "mai": "नमूना देखी",
        "bho": "नमूना देखी",
        "en": "View a sample",
    },
    "feature_customizer": {
        "hi": "लाइव कस्टमाइज़र",
        "mai": "लाइव कस्टमाइज़र",
        "bho": "लाइव कस्टमाइज़र",
        "en": "Live customizer",
    },
    "feature_customizer_desc": {
        "hi": "नाम, तारीख, स्थान और संस्कार तुरंत बदलें।",
        "mai": "नाम, तारीख, स्थान आ संस्कार तुरंत बदली।",
        "bho": "नाम, तारीख, स्थान आ संस्कार तुरंत बदली।",
        "en": "Change names, dates, venues and rituals instantly.",
    },
    "feature_whatsapp": {
        "hi": "सीधे व्हाट्सएप शेयर",
        "mai": "सीधे व्हाट्सएप शेयर",
        "bho": "सीधे व्हाट्सएप शेयर",
        "en": "Direct WhatsApp sharing",
    },
    "feature_whatsapp_desc": {
        "hi": "सोशल मीडिया पर पोस्ट करें, लिंक तुरंत पहुँचे।",
        "mai": "सोशल मीडिया पर पोस्ट करी, लिंक तुरंत पहुँची।",
        "bho": "सोशल मीडिया पर पोस्ट करी, लिंक तुरंत पहुँची।",
        "en": "Post on social media — the link reaches instantly.",
    },
    "feature_ritual": {
        "hi": "बिहारी संस्कार",
        "mai": "बिहारी संस्कार",
        "bho": "बिहारी संस्कार",
        "en": "Bihari rituals",
    },
    "feature_ritual_desc": {
        "hi": "तिलक, माटकोर, हल्दी, द्वार पूजा, जयमाला, कोहबर, प्रीतिभोज।",
        "mai": "तिलक, माटकोर, हल्दी, द्वार पूजा, जयमाला, कोहबर, प्रीतिभोज।",
        "bho": "तिलक, माटकोर, हल्दी, द्वार पूजा, जयमाला, कोहबर, प्रीतोज।",
        "en": "Tilak, Matkor, Haldi, Dwar Puja, Jaimala, Kohbar, Preeti Bhoj.",
    },
    "feature_lowbandwidth": {
        "hi": "कमज़ोर नेटवर्क पर भी तेज़",
        "mai": "कमज़ोर नेटवर्क पर भी तेज़",
        "bho": "कमज़ोर नेटवर्क पर भी तेज़",
        "en": "Fast even on a weak network",
    },
    "feature_lowbandwidth_desc": {
        "hi": "छोटी फ़ाइलें, तेज़ लोड, ऑफ़लाइन-रेडी SVG।",
        "mai": "छोटी फाइल, तेज़ लोड, ऑफ़लाइन-रेडी SVG।",
        "bho": "छोटी फाइल, तेज़ लोड, ऑफ़लाइन-रेडी SVG।",
        "en": "Tiny assets, fast loads, offline-ready SVG art.",
    },
    "stat_families": {
        "hi": "परिवार जुड़े",
        "mai": "परिवार जुड़ल",
        "bho": "परिवार जुड़ल",
        "en": "families connected",
    },
    "stat_rituals": {
        "hi": "संस्कार सज़े",
        "mai": "संस्कार सजल",
        "bho": "संस्कार सजल",
        "en": "rituals styled",
    },
    "stat_districts": {
        "hi": "ज़िले जुड़े",
        "mai": "जिला जुड़ल",
        "bho": "जिला जुड़ल",
        "en": "districts reached",
    },
    # --- Invitation page --------------------------------------------------
    "invite_welcome": {
        "hi": "आपका सादर आह्वान",
        "mai": "अहाँक सादर आह्वान",
        "bho": "आपके सादर आह्वान",
        "en": "You are cordially invited",
    },
    "invite_with_family": {
        "hi": "सपरिवार",
        "mai": "परिवार सहित",
        "bho": "परिवार सहित",
        "en": "with family",
    },
    "invite_you_are_invited": {
        "hi": "आपको आमंत्रित किया जाता है",
        "mai": "अहाँक आमंत्रित कैल जाता",
        "bho": "आपके आमंत्रित कैल जाता",
        "en": "You are invited to",
    },
    "invite_view_schedule": {
        "hi": "कार्यक्रम देखें",
        "mai": "कार्यक्रम देखी",
        "bho": "कार्यक्रम देखी",
        "en": "View the schedule",
    },
    "invite_rsvp": {
        "hi": "आगमन की पुष्टि करें",
        "mai": "आगमन के पुष्टि करी",
        "bho": "आगमन के पुष्टि करी",
        "en": "Confirm attendance",
    },
    "invite_send_blessing": {
        "hi": "आशीर्वाद भेजें",
        "mai": "आशीर्वाद भेजी",
        "bho": "आशीर्वाद भेजी",
        "en": "Send a blessing",
    },
    "invite_share": {
        "hi": "साझा करें",
        "mai": "साझा करी",
        "bho": "साझा करी",
        "en": "Share",
    },
    "door_title": {
        "hi": "कोहबर का दरवाज़ा",
        "mai": "कोहबर के दरवाज़ा",
        "bho": "कोहबर के दरवाज़ा",
        "en": "The Kohbar door",
    },
    "door_hint": {
        "hi": "दरवाज़ा खोलने के लिए स्पर्श करें",
        "mai": "दरवाज़ा खोलन खे स्पर्श करी",
        "bho": "दरवाज़ा खोलन खे स्पर्श करी",
        "en": "Tap the door to open it",
    },
    "audio_play": {
        "hi": "संगीत चलाएँ",
        "mai": "संगीत चलाई",
        "bho": "संगीत चलाई",
        "en": "Play music",
    },
    "audio_pause": {
        "hi": "संगीत रोकें",
        "mai": "संगीत रोकी",
        "bho": "संगीत रोकी",
        "en": "Pause music",
    },
    "audio_hint": {
        "hi": "मोबाइल डेटा बचाने के लिए संगीत पहले से बंद है।",
        "mai": "मोबाइल डेटा बचओ खातिर संगीत पहिले सँ बंद रहल।",
        "bho": "मोबाइल डेटा बचओ खातिर संगीत पहिले से बंद बा।",
        "en": "Music is off by default to save mobile data.",
    },
    "language_label": {
        "hi": "भाषा",
        "mai": "भाषा",
        "bho": "भाषा",
        "en": "Language",
    },
    "functions_title": {
        "hi": "संस्कार का क्रम",
        "mai": "संस्कार के क्रम",
        "bho": "संस्कार के क्रम",
        "en": "Order of rituals",
    },
    "label_date_time": {
        "hi": "तिथि व समय",
        "mai": "तिथि अ समय",
        "bho": "तिथि अ समय",
        "en": "Date & time",
    },
    "label_venue": {
        "hi": "स्थान",
        "mai": "स्थान",
        "bho": "स्थान",
        "en": "Venue",
    },
    "label_map": {
        "hi": "गूगल मैप्स पर देखें",
        "mai": "गूगल मैप्स पर देखी",
        "bho": "गूगल मैप्स पर देखी",
        "en": "Open in Google Maps",
    },
    "label_shloka": {
        "hi": "श्लोक",
        "mai": "श्लोक",
        "bho": "श्लोक",
        "en": "Shloka",
    },
    "guest_name_label": {
        "hi": "आपका नाम",
        "mai": "अहाँक नाम",
        "bho": "आपके नाम",
        "en": "Your name",
    },
    "guest_tag_label": {
        "hi": "परिवार / पक्ष",
        "mai": "परिवार / पक्ष",
        "bho": "परिवार / पक्ष",
        "en": "Family / side",
    },
    "guest_phone_label": {
        "hi": "मोबाइल नंबर",
        "mai": "मोबाइल नंबर",
        "bho": "मोबाइल नंबर",
        "en": "Mobile number",
    },
    "guest_count_label": {
        "hi": "कुल कितने आएँगे",
        "mai": "कुल कतन आइब",
        "bho": "कुल कतन आइब",
        "en": "How many will attend",
    },
    "rsvp_yes": {
        "hi": "आसा/आदर से आएँगे",
        "mai": "आसा/आदर सँ आइब",
        "bho": "आसा/आदर से आइब",
        "en": "Yes, with blessings",
    },
    "rsvp_no": {
        "hi": "स्नेह सहित क्षमा",
        "mai": "स्नेह सहित क्षमा",
        "bho": "स्नेह सहित क्षमा",
        "en": "Regretfully cannot attend",
    },
    "rsvp_message_label": {
        "hi": "वर-वधू के लिए शुभकामनाएँ",
        "mai": "वर-वधू के लिए शुभकामना",
        "bho": "वर-वधू के लिए शुभकामना",
        "en": "Blessings for the bride and groom",
    },
    "rsvp_submit": {
        "hi": "पुष्टि भेजें",
        "mai": "पुष्टि भेजी",
        "bho": "पुष्टि भेजी",
        "en": "Send confirmation",
    },
    "rsvp_success": {
        "hi": "धन्यवाद! आपका सादर आह्वान हमारे पास पहुँच गया।",
        "mai": "धन्यवाद! अहाँक सादर आह्वान हमर पास पहुँच गल।",
        "bho": "धन्यवाद! आपके सादर आह्वान हमार पास पहुँच गल।",
        "en": "Thank you! Your kind response has reached us.",
    },
    "rsvp_error": {
        "hi": "कृपया नाम और मोबाइल नंबर भरें।",
        "mai": "कृपया नाम अ मोबाइल नंबर भरी।",
        "bho": "कृपया नाम अ मोबाइल नंबर भरी।",
        "en": "Please fill in your name and mobile number.",
    },
    "bless_title": {
        "hi": "पान-लड्डू का आशीर्वाद",
        "mai": "पान-लड्डू के आशीर्वाद",
        "bho": "पान-लड्डू के आशीर्वाद",
        "en": "Send a Paan-Laddoo blessing",
    },
    "bless_send": {
        "hi": "आशीर्वाद भेजें",
        "mai": "आशीर्वाद भेजी",
        "bho": "आशीर्वाद भेजी",
        "en": "Send blessing",
    },
    "bless_success": {
        "hi": "आशीर्वाद पहुँच गया! पान-लड्डू के साथ आपका सादर।",
        "mai": "आशीर्वाद पहुँच गल! पान-लड्डू के साथ अहाँक सादर।",
        "bho": "आशीर्वाद पहुँच गल! पान-लड्डू के साथ आपके सादर।",
        "en": "Your blessing has arrived, with paan and laddoo!",
    },
    "share_whatsapp": {
        "hi": "व्हाट्सएप पर भेजें",
        "mai": "व्हाट्सएप पर भेजी",
        "bho": "व्हाट्सएप पर भेजी",
        "en": "Share on WhatsApp",
    },
    "share_copy": {
        "hi": "लिंक कॉपी करें",
        "mai": "लिंक कॉपी करी",
        "bho": "लिंक कॉपी करी",
        "en": "Copy link",
    },
    "share_copied": {
        "hi": "लिंक कॉपी हो गया",
        "mai": "लिंक कॉपी हो गल",
        "bho": "लिंक कॉपी हो गल",
        "en": "Link copied",
    },
    "view_count": {
        "hi": "बार देखा गया",
        "mai": "बार देखल गल",
        "bho": "बार देखल गल",
        "en": "views",
    },
    # --- Dashboard --------------------------------------------------------
    "dashboard_title": {
        "hi": "मेरे निमंत्रण",
        "mai": "हमर निमंत्रण",
        "bho": "हमर निमंत्रण",
        "en": "My Invitations",
    },
    "dashboard_empty": {
        "hi": "अभी कोई निमंत्रण नहीं बना। पहला निमंत्रण बनाएँ — बिल्कुल मुफ़्त।",
        "mai": "अखन कोनो निमंत्रण नहि बनल। पहिल निमंत्रण बनाउ — बिल्कुल मुफ़्त।",
        "bho": "अभी कोनो निमंत्रण नहि बनल। पहिल निमंत्रण बनाई — बिल्कुल मुफ़्त।",
        "en": "No invitation yet. Create your first — it is completely free.",
    },
    "dashboard_views": {
        "hi": "कुल बार देखा गया",
        "mai": "कुल बार देखल गल",
        "bho": "कुल बार देखल गल",
        "en": "Total views",
    },
    "dashboard_rsvps": {
        "hi": "पुष्टि",
        "mai": "पुष्टि",
        "bho": "पुष्टि",
        "en": "RSVPs",
    },
    "dashboard_published": {
        "hi": "प्रकाशित",
        "mai": "प्रकाशित",
        "bho": "प्रकाशित",
        "en": "Published",
    },
    "dashboard_draft": {
        "hi": "ड्राफ़्ट",
        "mai": "ड्राफ़्ट",
        "bho": "ड्राफ़्ट",
        "en": "Draft",
    },
    "dashboard_share": {
        "hi": "व्हाट्सएप संदेश",
        "mai": "व्हाट्सएप संदेश",
        "bho": "व्हाट्सएप संदेश",
        "en": "WhatsApp message",
    },
    "dashboard_copy_link": {
        "hi": "लिंक कॉपी करें",
        "mai": "लिंक कॉपी करी",
        "bho": "लिंक कॉपी करी",
        "en": "Copy link",
    },
    "dashboard_edit": {
        "hi": "संपादित करें",
        "mai": "संपादित करी",
        "bho": "संपादित करी",
        "en": "Edit",
    },
    "dashboard_delete": {
        "hi": "हटाएँ",
        "mai": "हटाई",
        "bho": "हटाई",
        "en": "Delete",
    },
    "dashboard_leads": {
        "hi": "लीड",
        "mai": "लीड",
        "bho": "लीड",
        "en": "Leads",
    },
    "dashboard_view_site": {
        "hi": "निमंत्रण देखें",
        "mai": "निमंत्रण देखी",
        "bho": "निमंत्रण देखी",
        "en": "View invitation",
    },
    "functions_manage": {
        "hi": "संस्कार प्रबंधित करें",
        "mai": "संस्कार प्रबंधित करी",
        "bho": "संस्कार प्रबंधित करी",
        "en": "Manage rituals",
    },
    "add_function": {
        "hi": "संस्कार जोड़ें",
        "mai": "संस्कार जोड़ी",
        "bho": "संस्कार जोड़ी",
        "en": "Add ritual",
    },
    "guest_list": {
        "hi": "आमंत्रित मेहमान",
        "mai": "आमंत्रित मेहमान",
        "bho": "आमंत्रित मेहमान",
        "en": "Guest list",
    },
    # --- Forms ------------------------------------------------------------
    "form_bride": {
        "hi": "वधू का नाम",
        "mai": "वधू के नाम",
        "bho": "वधू के नाम",
        "en": "Bride's name",
    },
    "form_groom": {
        "hi": "वर का नाम",
        "mai": "वर के नाम",
        "bho": "वर के नाम",
        "en": "Groom's name",
    },
    "form_event_title": {
        "hi": "शीर्षक",
        "mai": "शीर्षक",
        "bho": "शीर्षक",
        "en": "Event title",
    },
    "form_family_head": {
        "hi": "परिवार के मुखिया का नाम",
        "mai": "परिवार के मुखिया के नाम",
        "bho": "परिवार के मुखिया के नाम",
        "en": "Head of the family",
    },
    "form_native_place": {
        "hi": "ग्राम / ज़िला",
        "mai": "ग्राम / जिला",
        "bho": "ग्राम / जिला",
        "en": "Village / district",
    },
    "form_host_phone": {
        "hi": "संपर्क मोबाइल",
        "mai": "संपर्क मोबाइल",
        "bho": "संपर्क मोबाइल",
        "en": "Contact mobile",
    },
    "form_date": {
        "hi": "विवाह की तिथि",
        "mai": "विवाह के तिथि",
        "bho": "विवाह के तिथि",
        "en": "Wedding date",
    },
    "form_language": {
        "hi": "मुख्य भाषा",
        "mai": "मुख्य भाषा",
        "bho": "मुख्य भाषा",
        "en": "Primary language",
    },
    "form_welcome_message": {
        "hi": "स्वागत संदेश",
        "mai": "स्वागत संदेश",
        "bho": "स्वागत संदेश",
        "en": "Welcome message",
    },
    "form_shloka": {
        "hi": "श्लोक",
        "mai": "श्लोक",
        "bho": "श्लोक",
        "en": "Shloka",
    },
    "form_template": {
        "hi": "थीम",
        "mai": "थीम",
        "bho": "थीम",
        "en": "Theme",
    },
    "form_venue": {
        "hi": "स्थान का नाम",
        "mai": "स्थान के नाम",
        "bho": "स्थान के नाम",
        "en": "Venue name",
    },
    "form_address": {
        "hi": "पूरा पता",
        "mai": "पूरा पता",
        "bho": "पूरा पता",
        "en": "Full address",
    },
    "form_maps_url": {
        "hi": "गूगल मैप्स लिंक",
        "mai": "गूगल मैप्स लिंक",
        "bho": "गूगल मैप्स लिंक",
        "en": "Google Maps link",
    },
    "form_function_type": {
        "hi": "संस्कार",
        "mai": "संस्कार",
        "bho": "संस्कार",
        "en": "Ritual",
    },
    "form_function_time": {
        "hi": "तिथि व समय",
        "mai": "tisthि अ समय",
        "bho": "तिथि अ समय",
        "en": "Date & time",
    },
    "form_submit": {
        "hi": "सहेजें",
        "mai": "सहेजी",
        "bho": "सहेजी",
        "en": "Save",
    },
    "form_cancel": {
        "hi": "रद्द",
        "mai": "रद्द",
        "bho": "रद्द",
        "en": "Cancel",
    },
    # --- Lead capture -----------------------------------------------------
    "lead_title": {
        "hi": "निजी निमंत्रण चाहिए?",
        "mai": "निजी निमंत्रण चाही?",
        "bho": "निजी निमंत्रण चाही?",
        "en": "Want a customised invitation?",
    },
    "lead_body": {
        "hi": "अपना मोबाइल नंबर भेजें, हम बनाकर देंगे — बिल्कुल मुफ़्त।",
        "mai": "अपन मोबाइल नंबर भेजी, हम बनाकर दीब — बिल्कुल मुफ़्त।",
        "bho": "आपन मोबाइल नंबर भेजी, हम बनाकर दीब — बिल्कुल मुफ़्त।",
        "en": "Send your mobile number and we will build it for you — completely free.",
    },
    "lead_submit": {
        "hi": "भेजें",
        "mai": "भेजी",
        "bho": "भेजी",
        "en": "Send",
    },
    "lead_success": {
        "hi": "धन्यवाद! हम जल्द ही आपसे संपर्क करेंगे।",
        "mai": "धन्यवाद! हम जल्द ही अहाँसँ संपर्क करीब।",
        "bho": "धन्यवाद! हम जल्द ही आपसे संपर्क करीब।",
        "en": "Thank you! We will reach out very soon.",
    },
    # --- Footer -----------------------------------------------------------
    "footer_tagline": {
        "hi": "गर बैठे एक क्लिक में भेजें स्नेह निमंत्रण — सभी संस्कार, लोक गीत और गूगल मैप्स के साथ।",
        "mai": "घर बैठि एक क्लिक में भेजी स्नेह निमंत्रण — सभी संस्कार, लोक गीत आ गूगल मैप्स के साथ।",
        "bho": "घर बैठे एक क्लिक में भेजी स्नेह निमंत्रण — सभी संस्कार, लोक गीत आ गूगल मैप्स के साथ।",
        "en": "Send heartfelt invitations in one tap — every ritual, folk song and Google Map included.",
    },
    "footer_rights": {
        "hi": "सर्वाधिकार सुरक्षित।",
        "mai": "सर्वाधिकार सुरक्षित।",
        "bho": "सर्वाधिकार सुरक्षित।",
        "en": "All rights reserved.",
    },
    "footer_dialects": {
        "hi": "ग्रामीन भाषा",
        "mai": "ग्रामीन भाषा",
        "bho": "ग्रामीन भाषा",
        "en": "Gramin Bhasha",
    },
}


def get_string(key: str, lang: str = DEFAULT_LANG) -> str:
    """Return the translation for ``key`` falling back to Hindi then English."""

    entry = STRINGS.get(key)
    if not entry:
        return key
    return entry.get(lang) or entry.get(DEFAULT_LANG) or entry.get("en", key)


# ---------------------------------------------------------------------------
# Wedding website builder — UI copy
# ---------------------------------------------------------------------------
SITE_STRINGS: dict[str, dict[str, str]] = {
    "site_cta_create": {
        "hi": "मेरी वेडिंग वेबसाइट बनाएँ",
        "mai": "हमर वेडिंग वेबसाइट बनाउ",
        "bho": "हमर वेडिंग वेबसाइट बनाई",
        "en": "Create My Wedding Website",
    },
    "site_cta_upload": {
        "hi": "निमंत्रण कार्ड अपलोड करें",
        "mai": "निमंत्रण कार्ड अपलोड करीं",
        "bho": "निमंत्रण कार्ड अपलोड करीं",
        "en": "Upload your invitation card",
    },
    "site_cta_manual": {
        "hi": "विवरण स्वयं भरें",
        "mai": "विवरण स्वयं भरीं",
        "bho": "विवरण स्वयं भरीं",
        "en": "Enter the details manually",
    },
    "site_step_upload": {
        "hi": "अपलोड",
        "mai": "अपलोड",
        "bho": "अपलोड",
        "en": "Upload",
    },
    "site_step_details": {
        "hi": "विवरण",
        "mai": "विवरण",
        "bho": "विवरण",
        "en": "Details",
    },
    "site_step_theme": {
        "hi": "थीम",
        "mai": "थीम",
        "bho": "थीम",
        "en": "Theme",
    },
    "site_step_schedule": {
        "hi": "कार्यक्रम",
        "mai": "कार्यक्रम",
        "bho": "कार्यक्रम",
        "en": "Schedule",
    },
    "site_step_photos": {
        "hi": "तस्वीरें",
        "mai": "तस्वीर",
        "bho": "तस्वीर",
        "en": "Photos",
    },
    "site_step_customise": {
        "hi": "सजावट",
        "mai": "सजावट",
        "bho": "सजावट",
        "en": "Customise",
    },
    "site_step_preview": {
        "hi": "पूर्वावलोकन",
        "mai": "पूर्वावलोकन",
        "bho": "पूर्वावलोकन",
        "en": "Preview",
    },
    "site_step_publish": {
        "hi": "प्रकाशित",
        "mai": "प्रकाशित",
        "bho": "प्रकाशित",
        "en": "Publish",
    },
    "site_review_title": {
        "hi": "निमंत्रण से मिली जानकारी जाँचें",
        "mai": "निमंत्रण से मिलल जानकारी जाँचीं",
        "bho": "निमंत्रण से मिलल जानकारी जाँचीं",
        "en": "Check the details we found",
    },
    "site_review_hint": {
        "hi": "हमने आपके निमंत्रण को पढ़ा है। कृपया जो गलत हो उसे ठीक करें।",
        "mai": "हमनि अहाँ के निमंत्रण पढ़ल रहल छी। कृपया जे गलत छी ठीक करीं।",
        "bho": "हमनि आपके निमंत्रण पढ़ल रहल बा। कृपया जे गलत बा ठीक करीं।",
        "en": "We read your invitation card. Please correct anything that is wrong.",
    },
    "site_from_invitation": {
        "hi": "निमंत्रण से",
        "mai": "निमंत्रण से",
        "bho": "निमंत्रण से",
        "en": "From your invitation",
    },
    "site_confirmed": {
        "hi": "आपकी पुष्टि",
        "mai": "अहाँ के पुष्टि",
        "bho": "आपके पुष्टि",
        "en": "Confirmed by you",
    },
    "site_needs_review": {
        "hi": "जाँच बाकी है",
        "mai": "जाँच बाकी छी",
        "bho": "जाँच बाकी बा",
        "en": "Needs your review",
    },
    "site_no_ocr": {
        "hi": "हम यह नहीं पढ़ सके — कृपया खुद भरें।",
        "mai": "हम ई नहि पढ़ सकल — कृपया स्वयं भरीं।",
        "bho": "हम ई नहि पढ़ सकल — कृपया स्वयं भरीं।",
        "en": "We could not read this automatically — please fill it in.",
    },
    "site_save_continue": {
        "hi": "सहेजें और आगे बढ़ें",
        "mai": "सहेजीं आ आगाँ बढ़ीं",
        "bho": "सहेजीं आ आगाँ बढ़ीं",
        "en": "Save and continue",
    },
    "site_theme_title": {
        "hi": "अपनी वेबसाइट का थीम चुनें",
        "mai": "अपन वेबसाइट के थीम चुनीं",
        "bho": "अपन वेबसाइट के थीम चुनीं",
        "en": "Choose your website theme",
    },
    "site_theme_selected": {
        "hi": "चुनी गई",
        "mai": "चुनल गई",
        "bho": "चुनल गई",
        "en": "Selected",
    },
    "site_events_title": {
        "hi": "वेडिंग का कार्यक्रम",
        "mai": "वेडिंग के कार्यक्रम",
        "bho": "वेडिंग के कार्यक्रम",
        "en": "Wedding schedule",
    },
    "site_add_event": {
        "hi": "कार्यक्रम जोड़ें",
        "mai": "कार्यक्रम जोड़ीं",
        "bho": "कार्यक्रम जोड़ीं",
        "en": "Add an event",
    },
    "site_photos_title": {
        "hi": "तस्वीरें",
        "mai": "तस्वीर",
        "bho": "तस्वीर",
        "en": "Photographs",
    },
    "site_add_photo": {
        "hi": "तस्वीर अपलोड करें",
        "mai": "तस्वीर अपलोड करीं",
        "bho": "तस्वीर अपलोड करीं",
        "en": "Upload a photo",
    },
    "site_customise_title": {
        "hi": "वेबसाइट सजाएँ",
        "mai": "वेबसाइट सजाउ",
        "bho": "वेबसाइट सजाई",
        "en": "Customise your website",
    },
    "site_preview_title": {
        "hi": "अपनी वेबसाइट देखें",
        "mai": "अपन वेबसाइट देखीं",
        "bho": "अपन वेबसाइट देखीं",
        "en": "Preview your website",
    },
    "site_missing_info": {
        "hi": "अभी यह जानकारी नहीं है",
        "mai": "अभी ई जानकारी नहि छी",
        "bho": "अभी ई जानकारी नहि बा",
        "en": "Missing information",
    },
    "site_publish_title": {
        "hi": "वेडिंग वेबसाइट प्रकाशित करें",
        "mai": "वेडिंग वेबसाइट प्रकाशित करीं",
        "bho": "वेडिंग वेबसाइट प्रकाशित करीं",
        "en": "Publish your wedding website",
    },
    "site_publish_confirm": {
        "hi": "हाँ, मेरी वेडिंग वेबसाइट प्रकाशित करें",
        "mai": "हाँ, हमर वेडिंग वेबसाइट प्रकाशित करीं",
        "bho": "हाँ, हमर वेडिंग वेबसाइट प्रकाशित करीं",
        "en": "Yes, publish my wedding website",
    },
    "site_publish_private_note": {
        "hi": "अभी यह वेबसाइट सिर्फ आपको दिखती है। प्रकाशित करने के बाद सबको दिखेगी।",
        "mai": "अभी ई वेबसाइट सिर्फ अहाँ के दिखी। प्रकाशित करीं बाद सबके दिखी।",
        "bho": "अभी ई वेबसाइट सिर्फ आपके दिखी। प्रकाशित करीं बाद सबके दिखी।",
        "en": "This website is private for now. It becomes public only after you publish it.",
    },
    "site_share_title": {
        "hi": "वेडिंग वेबसाइट साझा करें",
        "mai": "वेडिंग वेबसाइट साझा करीं",
        "bho": "वेडिंग वेबसाइट साझा करीं",
        "en": "Share your wedding website",
    },
    "site_copy_link": {
        "hi": "लिंक कॉपी करें",
        "mai": "लिंक कॉपी करीं",
        "bho": "लिंक कॉपी करीं",
        "en": "Copy link",
    },
    "site_share_whatsapp": {
        "hi": "WhatsApp पर भेजें",
        "mai": "WhatsApp पर भेजीं",
        "bho": "WhatsApp पर भेजीं",
        "en": "Share on WhatsApp",
    },
    "site_open_site": {
        "hi": "वेबसाइट खोलें",
        "mai": "वेबसाइट खोलीं",
        "bho": "वेबसाइट खोलीं",
        "en": "Open website",
    },
    "site_unpublish": {
        "hi": "वेबसाइट ऑफ़लाइन करें",
        "mai": "वेबसाइट ऑफलाइन करीं",
        "bho": "वेबसाइट ऑफलाइन करीं",
        "en": "Take the website offline",
    },
    "site_delete_title": {
        "hi": "वेबसाइट मिटाएँ",
        "mai": "वेबसाइट मिटाउ",
        "bho": "वेबसाइट मिटाई",
        "en": "Delete this website",
    },
    "site_rsvp_title": {
        "hi": "क्या आप पहुँचेंगे?",
        "mai": "क्या अहाँ पहुँचीं?",
        "bho": "क्या आप पहुँचीं?",
        "en": "Will you join us?",
    },
    "site_rsvp_yes": {
        "hi": "हाँ, पहुँचूँगा/गी",
        "mai": "हाँ, पहुँचीं",
        "bho": "हाँ, पहुँचीं",
        "en": "Yes, I will attend",
    },
    "site_rsvp_no": {
        "hi": "नहीं, पहुँच नहीं सकूँगा/गी",
        "mai": "नहि, पहुँच नहि सकबीं",
        "bho": "नहि, पहुँच नहि सकबीं",
        "en": "Sorry, I cannot attend",
    },
    "site_rsvp_submit": {
        "hi": "जवाब भेजें",
        "mai": "जवाब भेजीं",
        "bho": "जवाब भेजीं",
        "en": "Send my response",
    },
    "site_countdown_title": {
        "hi": "शादी तक बाकी",
        "mai": "शादी तक बाकी",
        "bho": "शादी तक बाकी",
        "en": "Counting down to the wedding",
    },
    "site_story_title": {
        "hi": "हमारी कहानी",
        "mai": "हमर कहानी",
        "bho": "हमर कहानी",
        "en": "Our story",
    },
    "site_schedule_title": {
        "hi": "कार्यक्रम",
        "mai": "कार्यक्रम",
        "bho": "कार्यक्रम",
        "en": "Wedding schedule",
    },
    "site_gallery_title": {
        "hi": "तस्वीरें",
        "mai": "तस्वीर",
        "bho": "तस्वीर",
        "en": "Gallery",
    },
    "site_venue_title": {
        "hi": "स्थान",
        "mai": "स्थान",
        "bho": "स्थान",
        "en": "Venue",
    },
    "site_directions": {
        "hi": "रास्ता देखें",
        "mai": "रास्ता देखीं",
        "bho": "रास्ता देखीं",
        "en": "Get directions",
    },
    "site_family_title": {
        "hi": "परिवार की शुभकामनाएँ",
        "mai": "परिवार के शुभकामनाएँ",
        "bho": "परिवार के शुभकामनाएँ",
        "en": "Family greetings",
    },
    "site_contact_title": {
        "hi": "संपर्क",
        "mai": "संपर्क",
        "bho": "संपर्क",
        "en": "Contact",
    },
    "site_welcome_title": {
        "hi": "सादर आमंत्रण",
        "mai": "सादर आमंत्रण",
        "bho": "सादर आमंत्रण",
        "en": "You are warmly invited",
    },
    "site_dashboard_empty": {
        "hi": "अभी कोई वेडिंग वेबसाइट नहीं है।",
        "mai": "अभी कोनो वेडिंग वेबसाइट नहि छी।",
        "bho": "अभी कोई वेडिंग वेबसाइट नहि बा।",
        "en": "You have not created a wedding website yet.",
    },
    "site_rsvp_responses": {
        "hi": "जवाब",
        "mai": "जवाब",
        "bho": "जवाब",
        "en": "Responses",
    },
    "site_export_csv": {
        "hi": "CSV में डाउनलोड करें",
        "mai": "CSV में डाउनलोड करीं",
        "bho": "CSV में डाउनलोड करीं",
        "en": "Download CSV",
    },
    "site_dashboard_back": {
        "hi": "मेरी सभी वेबसाइट",
        "mai": "हमर सभी वेबसाइट",
        "bho": "हमर सभी वेबसाइट",
        "en": "All my websites",
    },
    "site_group_couple": {
        "hi": "वर और वधू",
        "mai": "वर आ वधू",
        "bho": "वर आ वधू",
        "en": "The couple",
    },
    "site_group_wedding": {
        "hi": "शादी की जानकारी",
        "mai": "शादी के जानकारी",
        "bho": "शादी के जानकारी",
        "en": "Wedding details",
    },
    "site_group_story": {
        "hi": "कहानी और संदेश",
        "mai": "कहानी आ संदेश",
        "bho": "कहानी आ संदेश",
        "en": "Story and messages",
    },
    "site_group_venue": {
        "hi": "स्थान",
        "mai": "स्थान",
        "bho": "स्थान",
        "en": "Venue",
    },
    "site_group_contact": {
        "hi": "संपर्क",
        "mai": "संपर्क",
        "bho": "संपर्क",
        "en": "Contact",
    },
    "site_theme_accents": {
        "hi": "थीम के रंग",
        "mai": "थीम के रंग",
        "bho": "थीम के रंग",
        "en": "Theme colours",
    },
    "site_photo_kinds": {
        "hi": "तस्वीर का प्रकार",
        "mai": "तस्वीर के प्रकार",
        "bho": "तस्वीर के प्रकार",
        "en": "Photo type",
    },
    "site_events_empty": {
        "hi": "अभी कोई कार्यक्रम नहीं जोड़ा गया।",
        "mai": "अभी कोनो कार्यक्रम नहि जोड़ल गई।",
        "bho": "अभी कोई कार्यक्रम नहि जोड़ल गया।",
        "en": "No event has been added yet.",
    },
    "site_photos_empty": {
        "hi": "अभी कोई तस्वीर नहीं जोड़ी गई।",
        "mai": "अभी कोनो तस्वीर नहि जोड़ल गई।",
        "bho": "अभी कोई तस्वीर नहि जोड़ल गई।",
        "en": "No photograph has been added yet.",
    },
    "site_rsvps_empty": {
        "hi": "अभी कोई जवाब नहीं आया।",
        "mai": "अभी कोनो जवाब नहि आईल।",
        "bho": "अभी कोई जवाब नहि आईल।",
        "en": "No response has come in yet.",
    },
    "site_delete_warning": {
        "hi": "इस वेबसाइट के सारे फ़ोटो, कार्यक्रम और RSVP हमेशा के लिए मिट जाएँगे।",
        "mai": "ई वेबसाइट के सभे फोटो, कार्यक्रम आ RSVP हमेशा खाति मिट जाइं।",
        "bho": "ई वेबसाइट के सभे फोटो, कार्यक्रम आ RSVP हमेशा खाति मिट जाईं।",
        "en": "Every photo, event and RSVP of this website will be deleted for good.",
    },
    "site_published_on": {
        "hi": "प्रकाशित",
        "mai": "प्रकाशित",
        "bho": "प्रकाशित",
        "en": "Published",
    },
    "site_views": {
        "hi": "कुल बार देखा गया",
        "mai": "कुल बार देखल गई",
        "bho": "कुल बार देखल गई",
        "en": "Total views",
    },
    "site_guests_coming": {
        "hi": "आने वाले मेहमान",
        "mai": "आवे वाला मेहमान",
        "bho": "आवे वाला मेहमान",
        "en": "Guests coming",
    },
    "site_source_invitation": {
        "hi": "मूल निमंत्रण डाउनलोड करें",
        "mai": "मूल निमंत्रण डाउनलोड करीं",
        "bho": "मूल निमंत्रण डाउनलोड करीं",
        "en": "Download the original invitation",
    },
    "site_back_to_step": {
        "hi": "पिछले चरण पर लौटें",
        "mai": "पिछले चरण पर लौटीं",
        "bho": "पिछले चरण पर लौटीं",
        "en": "Back to the previous step",
    },
    "site_choose_event": {
        "hi": "बदलने के लिए कार्यक्रम चुनें",
        "mai": "बदलीं खाति कार्यक्रम चुनीं",
        "bho": "बदलीं खाति कार्यक्रम चुनीं",
        "en": "Choose an event to edit",
    },
    "site_delete_event": {
        "hi": "हटाएँ",
        "mai": "हटाउ",
        "bho": "हटाई",
        "en": "Remove",
    },
    "site_edit": {
        "hi": "बदलें",
        "mai": "बदलीं",
        "bho": "बदलीं",
        "en": "Edit",
    },
    "site_delete_photo": {
        "hi": "तस्वीर हटाएँ",
        "mai": "तस्वीर हटाउ",
        "bho": "तस्वीर हटाई",
        "en": "Remove photo",
    },
    "site_delete_rsvp": {
        "hi": "जवाब हटाएँ",
        "mai": "जवाब हटाउ",
        "bho": "जवाब हटाई",
        "en": "Remove response",
    },
    "site_couple_line": {
        "hi": "शादी का निमंत्रण",
        "mai": "शादी के निमंत्रण",
        "bho": "शादी के निमंत्रण",
        "en": "The wedding of",
    },
    "site_days": {
        "hi": "दिन",
        "mai": "दिन",
        "bho": "दिन",
        "en": "Days",
    },
    "site_hours": {
        "hi": "घंटे",
        "mai": "घंटा",
        "bho": "घंटा",
        "en": "Hours",
    },
    "site_minutes": {
        "hi": "मिनट",
        "mai": "मिनट",
        "bho": "मिनट",
        "en": "Minutes",
    },
    "site_seconds": {
        "hi": "सेकंड",
        "mai": "सेकेन्ड",
        "bho": "सेकेन्ड",
        "en": "Seconds",
    },
    "site_map_note": {
        "hi": "नक्शा खोलने के लिए बटन दबाएँ।",
        "mai": "नक्सा खोलीं खाति बटन दबाउ।",
        "bho": "नक्सा खोलीं खाति बटन दबाईं।",
        "en": "Tap the button to open the map.",
    },
    "site_our_photos": {
        "hi": "हमारी तस्वीरें",
        "mai": "हमर तस्वीर",
        "bho": "हमर तस्वीर",
        "en": "Our photographs",
    },
    "site_guest_name": {
        "hi": "आपका नाम",
        "mai": "अहाँ के नाम",
        "bho": "आपके नाम",
        "en": "Your name",
    },
    "site_guest_phone": {
        "hi": "मोबाइल नंबर",
        "mai": "मोबाइल नंबर",
        "bho": "मोबाइल नंबर",
        "en": "Mobile number",
    },
    "site_thanks": {
        "hi": "धन्यवाद! आपका जवाब दर्ज हो गया।",
        "mai": "धन्यवाद! अहाँ के जवाब दर्ज हो गई।",
        "bho": "धन्यवाद! आपके जवाब दर्ज हो गई।",
        "en": "Thank you! Your response has been recorded.",
    },
}


STRINGS.update(SITE_STRINGS)


# ---------------------------------------------------------------------------
# Form fields — labels, placeholders and help texts follow the active dialect
# ---------------------------------------------------------------------------
FORM_LABELS: dict[str, dict[str, str]] = {
    # --- Account / authentication -----------------------------------------
    "username": {
        "hi": "उपयोगकर्ता नाम",
        "mai": "उपयोगकर्ता नाम",
        "bho": "यूजर नाम",
        "en": "Username",
    },
    "password": {
        "hi": "पासवर्ड",
        "mai": "पासवर्ड",
        "bho": "पासवर्ड",
        "en": "Password",
    },
    "password1": {
        "hi": "नया पासवर्ड",
        "mai": "नया पासवर्ड",
        "bho": "नया पासवर्ड",
        "en": "New password",
    },
    "password2": {
        "hi": "पासवर्ड की पुष्टि",
        "mai": "पासवर्ड के पुष्टि",
        "bho": "पासवर्ड के पुष्टि",
        "en": "Confirm password",
    },
    "email": {
        "hi": "ईमेल पता",
        "mai": "ईमेल पता",
        "bho": "ईमेल पता",
        "en": "Email address",
    },
    "phone_number": {
        "hi": "मोबाइल नंबर",
        "mai": "मोबाइल नंबर",
        "bho": "मोबाइल नंबर",
        "en": "Mobile number",
    },
    "first_name": {
        "hi": "पहला नाम",
        "mai": "पहिल नाम",
        "bho": "पहिल नाम",
        "en": "First name",
    },
    "last_name": {
        "hi": "उपनाम",
        "mai": "उपनाम",
        "bho": "उपनाम",
        "en": "Last name",
    },
    "home_district": {
        "hi": "गृह ज़िला",
        "mai": "गृह जिला",
        "bho": "गृह जिला",
        "en": "Home district",
    },
    # --- RSVP -------------------------------------------------------------
    "guest_name": {
        "hi": "आपका नाम",
        "mai": "अहाँ के नाम",
        "bho": "आपका नाम",
        "en": "Your name",
    },
    "guest_phone": {
        "hi": "मोबाइल नंबर",
        "mai": "मोबाइल नंबर",
        "bho": "मोबाइल नंबर",
        "en": "Mobile number",
    },
    "guest_family_tag": {
        "hi": "परिवार का नाम",
        "mai": "परिवार के नाम",
        "bho": "परिवार के नाम",
        "en": "Family name",
    },
    "attending_status": {
        "hi": "आगमन",
        "mai": "आगमन",
        "bho": "आगमन",
        "en": "Attending",
    },
    "guest_count": {
        "hi": "कुल संख्या",
        "mai": "कुल संख्या",
        "bho": "कुल संख्या",
        "en": "Total guests",
    },
    "blessing_message": {        "hi": "वर-वधू के लिए शुभकामनाएँ",
        "mai": "वर-वधू खाति शुभकामनाएँ",
        "bho": "वर-वधू खाति शुभकामनाएँ",
        "en": "Blessings for the bride & groom",
    },
    # --- Virtual blessing --------------------------------------------------
    "kind": {
        "hi": "आशीर्वाद प्रकार",
        "mai": "आशीर्वाद प्रकार",
        "bho": "आशीर्वाद प्रकार",
        "en": "Blessing type",
    },
    "message": {
        "hi": "आपका संदेश",
        "mai": "आपक संदेश",
        "bho": "आपक संदेश",
        "en": "Your message",
    },
    # --- Lead capture ------------------------------------------------------
    "name": {
        "hi": "आपका नाम",
        "mai": "अहाँ के नाम",
        "bho": "आपका नाम",
        "en": "Your name",
    },
    "district": {
        "hi": "ज़िला",
        "mai": "जिला",
        "bho": "जिला",
        "en": "District",
    },
    "event_date": {
        "hi": "शादी की तारीख",
        "mai": "शादी के तारीख",
        "bho": "शादी के तारीख",
        "en": "Event date",
    },
    # --- Event editor ------------------------------------------------------
    "bride_name": {
        "hi": "वधू का नाम",
        "mai": "वधू के नाम",
        "bho": "वधू के नाम",
        "en": "Bride's name",
    },
    "groom_name": {
        "hi": "वर का नाम",
        "mai": "वर के नाम",
        "bho": "वर के नाम",
        "en": "Groom's name",
    },
    "event_title": {
        "hi": "निमंत्रण शीर्षक",
        "mai": "निमंत्रण शीर्षक",
        "bho": "निमंत्रण शीर्षक",
        "en": "Invitation title",
    },
    "family_head_name": {
        "hi": "परिवार के मुखिया",
        "mai": "परिवार के मुखिया",
        "bho": "परिवार के मुखिया",
        "en": "Head of the family",
    },
    "native_place": {
        "hi": "मूल गाँव / ज़िला",
        "mai": "मूल गाँव / जिला",
        "bho": "मूल गाँव / जिला",
        "en": "Native village / district",
    },
    "host_phone": {
        "hi": "मेहमानी फ़ोन नंबर",
        "mai": "मेहमानी फोन नंबर",
        "bho": "मेहमानी फोन नंबर",
        "en": "Host phone number",
    },
    "primary_language": {
        "hi": "मुख्य भाषा",
        "mai": "मुख्य भाषा",
        "bho": "मुख्य भाषा",
        "en": "Primary language",
    },
    "wedding_date": {
        "hi": "शादी की तारीख",
        "mai": "शादी के तारीख",
        "bho": "शादी के तारीख",
        "en": "Wedding date",
    },
    "template": {
        "hi": "थीम / टेम्पलेट",
        "mai": "थीम / टेम्पलेट",
        "bho": "थीम / टेम्पलेट",
        "en": "Theme / template",
    },
    "custom_shloka": {
        "hi": "श्लोक",
        "mai": "श्लोक",
        "bho": "श्लोक",
        "en": "Shloka",
    },
    "welcome_message": {
        "hi": "स्वागत संदेश",
        "mai": "स्वागत संदेश",
        "bho": "स्वागत संदेश",
        "en": "Welcome message",
    },
    # --- Ritual (event function) editor ------------------------------------
    "function_code": {
        "hi": "संस्कार",
        "mai": "संस्कार",
        "bho": "संस्कार",
        "en": "Ritual",
    },
    "function_name": {
        "hi": "संस्कार का नाम",
        "mai": "संस्कार के नाम",
        "bho": "संस्कार के नाम",
        "en": "Ritual name",
    },
    "date_and_time": {
        "hi": "तिथि और समय",
        "mai": "तिथि आ समय",
        "bho": "तिथि आ समय",
        "en": "Date & time",
    },
    "venue_name": {
        "hi": "स्थान का नाम",
        "mai": "स्थान के नाम",
        "bho": "स्थान के नाम",
        "en": "Venue name",
    },
    "address": {
        "hi": "पता",
        "mai": "पता",
        "bho": "पता",
        "en": "Address",
    },
    "google_maps_url": {
        "hi": "गूगल मैप्स लिंक",
        "mai": "गूगल मैप्स लिंक",
        "bho": "गूगल मैप्स लिंक",
        "en": "Google Maps link",
    },
}

FORM_PLACEHOLDERS: dict[str, dict[str, str]] = {
    "username": {
        "hi": "जैसे: aman.kumar",
        "mai": "जैसे: aman.kumar",
        "bho": "जइसे: aman.kumar",
        "en": "e.g. aman.kumar",
    },
    "email": {
        "hi": "आपका ईमेल",
        "mai": "अहाँ के ईमेल",
        "bho": "आपके ईमेल",
        "en": "your@email.com",
    },
    "phone_number": {
        "hi": "+91 98765 43210",
        "mai": "+91 98765 43210",
        "bho": "+91 98765 43210",
        "en": "+91 98765 43210",
    },
    "home_district": {
        "hi": "जैसे: दरभंगा",
        "mai": "जइसे: दरभंगा",
        "bho": "जइसे: दरभंगा",
        "en": "e.g. Darbhanga",
    },
    "guest_name": {
        "hi": "आपका नाम",
        "mai": "अहाँ के नाम",
        "bho": "आपका नाम",
        "en": "Your name",
    },
    "guest_phone": {
        "hi": "98765 43210",
        "mai": "98765 43210",
        "bho": "98765 43210",
        "en": "98765 43210",
    },
    "guest_family_tag": {
        "hi": "जैसे: शर्मा परिवार",
        "mai": "जइसे: शर्मा परिवार",
        "bho": "जइसे: शर्मा परिवार",
        "en": "e.g. Sharma family",
    },
    "blessing_message": {
        "hi": "वर-वधू के लिए शुभकामनाएँ",
        "mai": "वर-वधू खाति शुभकामनाएँ",
        "bho": "वर-वधू खाति शुभकामनाएँ",
        "en": "Blessings for the couple",
    },
    "message": {
        "hi": "आपका संदेश",
        "mai": "आपक संदेश",
        "bho": "आपक संदेश",
        "en": "Your message",
    },
    "name": {
        "hi": "आपका नाम",
        "mai": "अहाँ के नाम",
        "bho": "आपका नाम",
        "en": "Your name",
    },
    "district": {
        "hi": "जैसे: पटना",
        "mai": "जइसे: पटना",
        "bho": "जइसे: पटना",
        "en": "e.g. Patna",
    },
    "event_date": {
        "hi": "जैसे: 18/02/2026",
        "mai": "जइसे: 18/02/2026",
        "bho": "जइसे: 18/02/2026",
        "en": "e.g. 18/02/2026",
    },
    "bride_name": {
        "hi": "जैसे: प्रिया",
        "mai": "जइसे: प्रिया",
        "bho": "जइसे: प्रिया",
        "en": "e.g. Priya",
    },
    "groom_name": {
        "hi": "जैसे: अमन",
        "mai": "जइसे: अमन",
        "bho": "जइसे: अमन",
        "en": "e.g. Aman",
    },
    "event_title": {
        "hi": "जैसे: अमन व प्रिया",
        "mai": "जइसे: अमन व प्रिया",
        "bho": "जइसे: अमन व प्रिया",
        "en": "e.g. Aman weds Priya",
    },
    "family_head_name": {
        "hi": "जैसे: श्री रामकांत रॉय",
        "mai": "जइसे: श्री रामकांत रॉय",
        "bho": "जइसे: श्री रामकांत रॉय",
        "en": "e.g. Shri Ramakant Roy",
    },
    "native_place": {
        "hi": "जैसे: ग्राम नेहरा, जिला दरभंगा",
        "mai": "जइसे: ग्राम नेहरा, जिला दरभंगा",
        "bho": "जइसे: ग्राम नेहरा, जिला दरभंगा",
        "en": "e.g. Gram Nehra, Darbhanga",
    },
    "host_phone": {
        "hi": "+91 98765 43210",
        "mai": "+91 98765 43210",
        "bho": "+91 98765 43210",
        "en": "+91 98765 43210",
    },
    "venue_name": {
        "hi": "जैसे: मौर्या होटल, पटना",
        "mai": "जइसे: मौर्या होटल, पटना",
        "bho": "जइसे: मौर्या होटल, पटना",
        "en": "e.g. Maurya Hotel, Patna",
    },
    "address": {
        "hi": "पूरा पता",
        "mai": "पूरा पता",
        "bho": "पूरा पता",
        "en": "Full address",
    },
    "google_maps_url": {
        "hi": "https://maps.google.com/…",
        "mai": "https://maps.google.com/…",
        "bho": "https://maps.google.com/…",
        "en": "https://maps.google.com/…",
    },
}

FORM_HELP: dict[str, dict[str, str]] = {
    "password1": {
        "hi": "कम से कम 8 अक्षर, एक अंक और एक बड़ा अक्षर रखें।",
        "mai": "कम से कम 8 अक्षर, एक अंक आ एक बड़ अक्षर रखीं।",
        "bho": "कम से कम 8 अक्षर, एक अंक आ एक बड़ अक्षर रखीं।",
        "en": "Use at least 8 characters with a number and a capital letter.",
    },
    "password2": {
        "hi": "ऊपर वाला पासवर्ड दोबारा लिखें।",
        "mai": "ऊपर के पासवर्ड दोबारा लिखीं।",
        "bho": "ऊपर वाला पासवर्ड दोबारा लिखीं।",
        "en": "Re-type the password above to confirm.",
    },
}


# ---------------------------------------------------------------------------
# Wedding website builder — field labels
# ---------------------------------------------------------------------------
SITE_FORM_LABELS: dict[str, dict[str, str]] = {
    "invitation": {
        "hi": "निमंत्रण कार्ड",
        "mai": "निमंत्रण कार्ड",
        "bho": "निमंत्रण कार्ड",
        "en": "Invitation card",
    },
    "acknowledgement": {
        "hi": "मैं इस निमंत्रण का मालिक हूँ और इसे प्रोसेस करने की अनुमति देता/देती हूँ",
        "mai": "हम ई निमंत्रण के मालिक छी आ इए प्रोसेस करीं के अनुमति देतछी",
        "bho": "हम ई निमंत्रण के मालिक बा आ ईए प्रोसेस करीं के अनुमति देत बा",
        "en": "I own this invitation and allow it to be processed",
    },
    "bride_name": {
        "hi": "वधू का नाम",
        "mai": "वधू के नाम",
        "bho": "वधू के नाम",
        "en": "Bride's name",
    },
    "groom_name": {
        "hi": "वर का नाम",
        "mai": "वर के नाम",
        "bho": "वर के नाम",
        "en": "Groom's name",
    },
    "bride_display_name": {
        "hi": "वधू का अंग्रेज़ी नाम (वैकल्पिक)",
        "mai": "वधू के अंग्रेजी नाम (वैकल्पिक)",
        "bho": "वधू के अंग्रेजी नाम (वैकल्पिक)",
        "en": "Bride's Latin spelling (optional)",
    },
    "groom_display_name": {
        "hi": "वर का अंग्रेज़ी नाम (वैकल्पिक)",
        "mai": "वर के अंग्रेजी नाम (वैकल्पिक)",
        "bho": "वर के अंग्रेजी नाम (वैकल्पिक)",
        "en": "Groom's Latin spelling (optional)",
    },
    "wedding_date": {
        "hi": "वेडिंग की तारीख",
        "mai": "वेडिंग के तारीख",
        "bho": "वेडिंग के तारीख",
        "en": "Wedding date",
    },
    "ceremony_time": {
        "hi": "शादी का समय",
        "mai": "शादी के समय",
        "bho": "शादी के समय",
        "en": "Ceremony time",
    },
    "timezone": {
        "hi": "समय क्षेत्र",
        "mai": "समय क्षेत्र",
        "bho": "समय क्षेत्र",
        "en": "Time zone",
    },
    "language": {
        "hi": "वेबसाइट की भाषा",
        "mai": "वेबसाइट के भाषा",
        "bho": "वेबसाइट के भाषा",
        "en": "Website language",
    },
    "introduction": {
        "hi": "परिचय",
        "mai": "परिचय",
        "bho": "परिचय",
        "en": "Introduction",
    },
    "welcome_message": {
        "hi": "स्वागत संदेश",
        "mai": "स्वागत संदेश",
        "bho": "स्वागत संदेश",
        "en": "Welcome message",
    },
    "story": {
        "hi": "हमारी कहानी",
        "mai": "हमर कहानी",
        "bho": "हमर कहानी",
        "en": "Our story",
    },
    "family_greetings": {
        "hi": "परिवार की शुभकामनाएँ",
        "mai": "परिवार के शुभकामनाएँ",
        "bho": "परिवार के शुभकामनाएँ",
        "en": "Family greetings",
    },
    "venue_name": {
        "hi": "स्थान का नाम",
        "mai": "स्थान के नाम",
        "bho": "स्थान के नाम",
        "en": "Venue name",
    },
    "venue_address": {
        "hi": "पता",
        "mai": "पता",
        "bho": "पता",
        "en": "Address",
    },
    "venue_city": {
        "hi": "शहर",
        "mai": "शहर",
        "bho": "शहर",
        "en": "City",
    },
    "venue_state": {
        "hi": "राज्य",
        "mai": "राज्य",
        "bho": "राज्य",
        "en": "State",
    },
    "venue_maps_url": {
        "hi": "गूगल मैप्स लिंक",
        "mai": "गूगल मैप्स लिंक",
        "bho": "गूगल मैप्स लिंक",
        "en": "Google Maps link",
    },
    "contact_name": {
        "hi": "संपर्क व्यक्ति",
        "mai": "संपर्क कर्ता",
        "bho": "संपर्क कर्ता",
        "en": "Contact person",
    },
    "contact_phone": {
        "hi": "संपर्क फ़ोन",
        "mai": "संपर्क फोन",
        "bho": "संपर्क फोन",
        "en": "Contact phone",
    },
    "contact_email": {
        "hi": "संपर्क ईमेल",
        "mai": "संपर्क ईमेल",
        "bho": "संपर्क ईमेल",
        "en": "Contact email",
    },
    "show_contact": {
        "hi": "संपर्क जानकारी वेबसाइट पर दिखाएँ",
        "mai": "संपर्क जानकारी वेबसाइट पर दिखाउ",
        "bho": "संपर्क जानकारी वेबसाइट पर दिखाई",
        "en": "Show contact details on the website",
    },
    "name": {
        "hi": "नाम",
        "mai": "नाम",
        "bho": "नाम",
        "en": "Name",
    },
    "date": {
        "hi": "तारीख",
        "mai": "तारीख",
        "bho": "तारीख",
        "en": "Date",
    },
    "start_time": {
        "hi": "शुरुआत का समय",
        "mai": "शुरुआत के समय",
        "bho": "शुरुआत के समय",
        "en": "Start time",
    },
    "end_time": {
        "hi": "समाप्ति का समय",
        "mai": "समाप्ति के समय",
        "bho": "समाप्ति के समय",
        "en": "End time",
    },
    "venue": {
        "hi": "स्थान",
        "mai": "स्थान",
        "bho": "स्थान",
        "en": "Venue",
    },
    "address": {
        "hi": "पता",
        "mai": "पता",
        "bho": "पता",
        "en": "Address",
    },
    "maps_url": {
        "hi": "गूगल मैप्स लिंक",
        "mai": "गूगल मैप्स लिंक",
        "bho": "गूगल मैप्स लिंक",
        "en": "Google Maps link",
    },
    "dress_code": {
        "hi": "ड्रेस कोड",
        "mai": "ड्रेस कोड",
        "bho": "ड्रेस कोड",
        "en": "Dress code",
    },
    "description": {
        "hi": "विवरण",
        "mai": "विवरण",
        "bho": "विवरण",
        "en": "Description",
    },
    "image": {
        "hi": "तस्वीर",
        "mai": "तस्वीर",
        "bho": "तस्वीर",
        "en": "Photograph",
    },
    "caption": {
        "hi": "कैप्शन",
        "mai": "कैप्शन",
        "bho": "कैप्शन",
        "en": "Caption",
    },
    "kind": {
        "hi": "तस्वीर का प्रकार",
        "mai": "तस्वीर के प्रकार",
        "bho": "तस्वीर के प्रकार",
        "en": "Photo type",
    },
    "theme": {
        "hi": "वेबसाइट थीम",
        "mai": "वेबसाइट थीम",
        "bho": "वेबसाइट थीम",
        "en": "Website theme",
    },
    "accent_color": {
        "hi": "एक्सेंट रंग",
        "mai": "एक्सेंट रंग",
        "bho": "एक्सेंट रंग",
        "en": "Accent colour",
    },
    "show_countdown": {
        "hi": "काउंटडाउन दिखाएँ",
        "mai": "काउंटडाउन दिखाउ",
        "bho": "काउंटडाउन दिखाई",
        "en": "Show the countdown",
    },
    "show_story": {
        "hi": "कहानी का हिस्सा दिखाएँ",
        "mai": "कहानी के हिस्सा दिखाउ",
        "bho": "कहानी के हिस्सा दिखाई",
        "en": "Show the story section",
    },
    "show_gallery": {
        "hi": "गैलरी दिखाएँ",
        "mai": "गैलरी दिखाउ",
        "bho": "गैलरी दिखाई",
        "en": "Show the gallery",
    },
    "show_family": {
        "hi": "परिवार का हिस्सा दिखाएँ",
        "mai": "परिवार के हिस्सा दिखाउ",
        "bho": "परिवार के हिस्सा दिखाई",
        "en": "Show the family section",
    },
    "show_rsvp": {
        "hi": "RSVP फ़ॉर्म दिखाएँ",
        "mai": "RSVP फॉर्म दिखाउ",
        "bho": "RSVP फॉर्म दिखाई",
        "en": "Show the RSVP form",
    },
    "rsvp_ask_guest_count": {
        "hi": "साथ आने वालों की संख्या पूछें",
        "mai": "संग आवे वाला के संख्या पूछीं",
        "bho": "साथ आवे वाला के संख्या पूछीं",
        "en": "Ask how many guests are coming",
    },
    "rsvp_ask_message": {
        "hi": "शुभकामना संदेश पूछें",
        "mai": "शुभकामना संदेश पूछीं",
        "bho": "शुभकामना संदेश पूछीं",
        "en": "Ask for a message",
    },
    "attending": {
        "hi": "क्या आप पहुँचेंगे?",
        "mai": "क्या अहाँ पहुँचीं?",
        "bho": "क्या आप पहुँचीं?",
        "en": "Attending",
    },
    "guest_count": {
        "hi": "कुल कितन लोग आबीं",
        "mai": "कुल कितन लोग आबीं",
        "bho": "कुल कितन लोग आबीं",
        "en": "Total number of guests",
    },
}


def _localised(table: dict[str, dict[str, str]], lang: str) -> dict[str, str]:
    """Flatten a per-field translation table for a single dialect."""

    return {
        name: (entry.get(lang) or entry.get(DEFAULT_LANG) or entry.get("en", name))
        for name, entry in table.items()
    }


def form_labels(lang: str = DEFAULT_LANG) -> dict[str, str]:
    """Field labels for the active dialect."""

    return _localised(FORM_LABELS, normalise(lang))


def form_placeholders(lang: str = DEFAULT_LANG) -> dict[str, str]:
    """Field placeholders for the active dialect."""

    return _localised(FORM_PLACEHOLDERS, normalise(lang))


def form_help(lang: str = DEFAULT_LANG) -> dict[str, str]:
    """Field help texts for the active dialect."""

    return _localised(FORM_HELP, normalise(lang))


def normalise(lang: str | None) -> str:
    if not lang:
        return DEFAULT_LANG
    lang = lang.strip().lower()
    if lang in CODE_TO_LEGACY:
        return lang
    if lang.upper() in LEGACY_TO_CODE:
        return LEGACY_TO_CODE[lang.upper()]
    return DEFAULT_LANG


class LocalizedFormMixin:
    """Switch a form's labels, placeholders and help texts to one dialect.

    Usage::

        form = MyForm(request.POST or None, lang=i18n.get_language(request))

    A form may carry its own ``label_table`` (a per-field translation table)
    so that two apps can use the same field name for two different things —
    for example a wedding *event* named ``name`` and a guest named ``name``.

    Fields that have no translation for the active dialect keep their original
    label, so the mixin is safe to use on forms with mixed field sets.
    """

    label_table: dict[str, dict[str, str]] | None = None

    def __init__(self, *args, lang: str | None = None, **kwargs):
        self.lang = normalise(lang or DEFAULT_LANG)
        super().__init__(*args, **kwargs)
        labels = form_labels(self.lang)
        table = self.label_table
        if table:
            labels = {**labels, **_localised(table, self.lang)}
        placeholders = form_placeholders(self.lang)
        helps = form_help(self.lang)
        for name, field in self.fields.items():
            if name in labels:
                field.label = labels[name]
            if name in helps:
                field.help_text = helps[name]
            if name in placeholders and isinstance(
                field.widget, (TextInput, Textarea)
            ):
                field.widget.attrs["placeholder"] = placeholders[name]


def get_language(request: HttpRequest) -> str:
    """Resolve the active dialect: query param → cookie → event → default."""

    lang = request.GET.get("lang")
    if lang:
        return normalise(lang)
    lang = request.COOKIES.get(LANG_COOKIE)
    if lang:
        return normalise(lang)
    event = getattr(request, "current_event", None)
    if event is not None:
        return normalise(CODE_TO_LEGACY.get(event.primary_language, event.primary_language))
    return DEFAULT_LANG
