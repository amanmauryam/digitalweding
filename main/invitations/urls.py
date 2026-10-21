from django.urls import path

from . import views

app_name = "invitations"

urlpatterns = [
    path("", views.home, name="home"),
    path("w/<slug:slug>/", views.event_detail, name="event_detail"),
    path("w/<slug:slug>/rsvp/", views.rsvp_create, name="rsvp_create"),
    path("w/<slug:slug>/blessing/", views.bless_create, name="bless_create"),
    path("api/<slug:slug>/functions/", views.api_event_functions, name="api_functions"),
    path("api/health/", views.api_health, name="api_health"),
    path("leads/", views.lead_create, name="lead_create"),
    path("language/", views.set_language, name="set_language"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/new/", views.event_create, name="event_create"),
    path("dashboard/<slug:slug>/edit/", views.event_edit, name="event_edit"),
    path("dashboard/<slug:slug>/delete/", views.event_delete, name="event_delete"),
    path("dashboard/<slug:slug>/functions/", views.event_functions, name="event_functions"),
    path(
        "dashboard/<slug:slug>/functions/<int:function_id>/delete/",
        views.function_delete,
        name="function_delete",
    ),
    path("dashboard/<slug:slug>/share/", views.event_share, name="event_share"),
    path("dashboard/<slug:slug>/guests/", views.event_guests, name="event_guests"),
    path("dashboard/<slug:slug>/preview/", views.event_preview, name="event_preview"),
]
