from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from . import bihari, i18n, services
from .forms import (
    BlessingForm,
    EventForm,
    EventFunctionForm,
    LeadForm,
    RSVPForm,
)
from .models import (
    CustomerEvent,
    EventFunction,
    GuestBlessing,
    InvitationCategory,
    LeadCapture,
    TemplateTheme,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def _apply_language_cookie(request, response):
    """Persist the dialect chosen through the one-tap switcher."""

    lang = i18n.get_language(request)
    if request.GET.get("lang"):
        response.set_cookie(i18n.LANG_COOKIE, lang, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return response


def _owned_event(request, slug: str) -> CustomerEvent:
    event = get_object_or_404(CustomerEvent, slug=slug)
    if event.user_id != request.user.id:
        raise Http404("आपको यह निमंत्रण नहीं दिखना चाहिए।")
    return event


# ---------------------------------------------------------------------------
# public pages
# ---------------------------------------------------------------------------
def home(request):
    categories = InvitationCategory.objects.all()
    templates = TemplateTheme.objects.filter(is_active=True).select_related("category")
    lead_form = LeadForm(request.POST or None, lang=i18n.get_language(request))
    if request.method == "POST":
        if lead_form.is_valid():
            lead = lead_form.save()
            response = render(
                request,
                "invitations/partials/lead_success.html",
                {"lead": lead},
                status=200,
            )
            return _apply_language_cookie(request, response)
        response = render(
            request,
            "invitations/partials/lead_form.html",
            {"form": lead_form},
            status=400,
        )
        return _apply_language_cookie(request, response)

    context = {
        "categories": categories,
        "templates": templates,
        "form": lead_form,
        "functions": bihari.FUNCTION_TEMPLATES,
        "palette": bihari.PALETTE,
        "features": [
            ("bamboo", "feature_customizer", "feature_customizer_desc"),
            ("paan", "feature_whatsapp", "feature_whatsapp_desc"),
            ("kalash", "feature_ritual", "feature_ritual_desc"),
            ("fish", "feature_lowbandwidth", "feature_lowbandwidth_desc"),
        ],
    }
    response = render(request, "invitations/home.html", context)
    return _apply_language_cookie(request, response)


def event_detail(request, slug: str):
    event = get_object_or_404(CustomerEvent, slug=slug, is_published=True)
    event.increment_views()

    guest_tag = (request.GET.get("guest") or "").strip()
    lang = i18n.get_language(request)
    rsvp_form = RSVPForm(
        initial={
            "guest_family_tag": guest_tag,
            "attending_status": "YES",
        },
        lang=lang,
    )
    blessing_form = BlessingForm(initial={"kind": "PAAN"}, lang=lang)
    blessing_modal_form = BlessingForm(prefix="modal", initial={"kind": "PAAN"}, lang=lang)

    context = {
        "event": event,
        "functions": event.functions_in_order(),
        "rsvp_form": rsvp_form,
        "blessing_form": blessing_form,
        "blessing_modal_form": blessing_modal_form,
        "guest_tag": guest_tag,
        "theme_tokens": services.template_preview_seed(event),
        "share_url": services.event_share_url(event, guest_tag or None),
        "whatsapp_message": services.build_whatsapp_message(event, guest_tag or None),
        "music_tracks": bihari.FUNCTION_TEMPLATES,
    }
    response = render(request, "invitations/event_detail.html", context)
    return _apply_language_cookie(request, response)


@require_POST
def rsvp_create(request, slug: str):
    event = get_object_or_404(CustomerEvent, slug=slug, is_published=True)
    form = RSVPForm(request.POST, lang=i18n.get_language(request))
    if form.is_valid():
        rsvp = form.save(commit=False)
        rsvp.event = event
        rsvp.save()
        response = render(
            request,
            "invitations/partials/rsvp_success.html",
            {"event": event, "rsvp": rsvp},
        )
    else:
        response = render(
            request,
            "invitations/partials/rsvp_form.html",
            {"form": form, "event": event},
            status=400,
        )
    return _apply_language_cookie(request, response)


@require_POST
def bless_create(request, slug: str):
    event = get_object_or_404(CustomerEvent, slug=slug, is_published=True)
    form = BlessingForm(request.POST, lang=i18n.get_language(request))
    if form.is_valid():
        blessing = form.save(commit=False)
        blessing.event = event
        blessing.save()
        response = render(
            request,
            "invitations/partials/blessing_success.html",
            {"event": event, "blessing": blessing},
        )
    else:
        response = render(
            request,
            "invitations/partials/blessing_form.html",
            {"form": form, "event": event},
            status=400,
        )
    return _apply_language_cookie(request, response)


@require_POST
def lead_create(request):
    form = LeadForm(request.POST, lang=i18n.get_language(request))
    if form.is_valid():
        lead = form.save()
        response = render(
            request, "invitations/partials/lead_success.html", {"lead": lead}
        )
    else:
        response = render(
            request, "invitations/partials/lead_form.html", {"form": form}, status=400
        )
    return _apply_language_cookie(request, response)


def set_language(request):
    """One-tap dialect switcher endpoint (keeps the visitor on the same page)."""

    lang = i18n.normalise(request.POST.get("lang") or request.GET.get("lang"))
    next_url = request.POST.get("next") or request.GET.get("next") or "/"
    response = HttpResponseRedirect(next_url)
    response.set_cookie(
        i18n.LANG_COOKIE, lang, max_age=60 * 60 * 24 * 365, samesite="Lax"
    )
    return response


# ---------------------------------------------------------------------------
# customer dashboard
# ---------------------------------------------------------------------------
@login_required
def dashboard(request):
    events = (
        CustomerEvent.objects.filter(user=request.user)
        .select_related("template")
        .prefetch_related("functions", "rsvps")
    )
    totals = {
        "events": events.count(),
        "views": sum(e.view_count for e in events),
        "rsvps": sum(e.total_rsvps for e in events),
        "guests": sum(e.attending_count for e in events),
    }
    context = {
        "events": events,
        "totals": totals,
        "leads": LeadCapture.objects.filter(is_contacted=False)[:5],
    }
    response = render(request, "invitations/dashboard.html", context)
    return _apply_language_cookie(request, response)


@login_required
def event_create(request):
    form = EventForm(request.POST or None, lang=i18n.get_language(request))
    if request.method == "POST" and form.is_valid():
        event = form.save(commit=False)
        event.user = request.user
        if not event.template_id:
            event.template = TemplateTheme.objects.filter(is_active=True).first()
        event.save()
        messages.success(request, "निमंत्रण तैयार है! अब संस्कार जोड़ें।")
        return redirect("invitations:event_functions", slug=event.slug)
    templates = list(TemplateTheme.objects.filter(is_active=True))
    context = {
        "form": form,
        "is_create": True,
        "templates": templates,
        "theme_palette": {str(t.id): t.preset for t in templates},
    }
    response = render(request, "invitations/event_form.html", context)
    return _apply_language_cookie(request, response)


@login_required
def event_edit(request, slug: str):
    event = _owned_event(request, slug)
    form = EventForm(request.POST or None, instance=event, lang=i18n.get_language(request))
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "बदलाव सहेज लिया गया।")
        return redirect("invitations:dashboard")
    templates = list(TemplateTheme.objects.filter(is_active=True))
    context = {"form": form, "event": event, "is_create": False,
               "templates": templates,
               "theme_palette": {str(t.id): t.preset for t in templates}}
    response = render(request, "invitations/event_form.html", context)
    return _apply_language_cookie(request, response)


@login_required
@require_POST
def event_delete(request, slug: str):
    event = _owned_event(request, slug)
    event.delete()
    messages.info(request, "निमंत्रण हटा दिया गया।")
    return redirect("invitations:dashboard")


@login_required
def event_functions(request, slug: str):
    event = _owned_event(request, slug)
    form = EventFunctionForm(request.POST or None, lang=i18n.get_language(request))
    if request.method == "POST" and form.is_valid():
        function = form.save(commit=False)
        function.event = event
        function.save()
        messages.success(request, f"{function.function_name} जुड़ गया।")
        return redirect("invitations:event_functions", slug=event.slug)
    context = {
        "event": event,
        "form": form,
        "functions": event.functions_in_order(),
        "templates": bihari.FUNCTION_TEMPLATES,
    }
    response = render(request, "invitations/event_functions.html", context)
    return _apply_language_cookie(request, response)


@login_required
@require_POST
def function_delete(request, slug: str, function_id: int):
    event = _owned_event(request, slug)
    function = get_object_or_404(EventFunction, pk=function_id, event=event)
    function.delete()
    return redirect("invitations:event_functions", slug=event.slug)


@login_required
def event_share(request, slug: str):
    event = _owned_event(request, slug)
    guest_tag = (request.GET.get("guest") or "").strip() or None
    message = services.build_whatsapp_message(event, guest_tag)
    context = {
        "event": event,
        "whatsapp_message": message,
        "share_url": services.event_share_url(event, guest_tag),
        "wa_link": services.whatsapp_link(message),
    }
    response = render(request, "invitations/event_share.html", context)
    return _apply_language_cookie(request, response)


@login_required
def event_guests(request, slug: str):
    event = _owned_event(request, slug)
    context = {
        "event": event,
        "rsvps": event.rsvps.all(),
        "blessings": event.blessings.all(),
    }
    response = render(request, "invitations/event_guests.html", context)
    return _apply_language_cookie(request, response)


@login_required
def event_preview(request, slug: str):
    """Preview the invitation as a guest would see it (works while drafting)."""

    event = _owned_event(request, slug)
    response = render(
        request,
        "invitations/event_detail.html",
        {
            "event": event,
            "functions": event.functions_in_order(),
            "rsvp_form": RSVPForm(initial={"attending_status": "YES"}, lang=i18n.get_language(request)),
            "blessing_form": BlessingForm(initial={"kind": "PAAN"}, lang=i18n.get_language(request)),
            "blessing_modal_form": BlessingForm(prefix="modal", initial={"kind": "PAAN"}, lang=i18n.get_language(request)),
            "guest_tag": "",
            "theme_tokens": services.template_preview_seed(event),
            "share_url": services.event_share_url(event),
            "whatsapp_message": services.build_whatsapp_message(event),
            "music_tracks": bihari.FUNCTION_TEMPLATES,
            "is_preview": True,
        },
    )
    return response


def api_event_functions(request, slug: str):
    """Tiny JSON endpoint used by the live customiser."""

    event = get_object_or_404(CustomerEvent, slug=slug, is_published=True)
    data = [
        {
            "code": f.function_code,
            "name": f.function_name,
            "devanagari": f.devanagari_name,
            "accent": f.accent_color,
            "music": f.folk_music,
            "date": f.date_and_time.isoformat(),
            "venue": f.venue_name,
            "address": f.address,
            "maps": f.google_maps_url,
        }
        for f in event.functions_in_order()
    ]
    return JsonResponse({"event": event.event_title, "functions": data})


def api_health(request):
    return JsonResponse({"status": "ok", "site": "digitalwedding"})


def redirect_to_event(request, slug: str):
    return HttpResponseRedirect(
        reverse("invitations:event_detail", kwargs={"slug": slug})
    )
