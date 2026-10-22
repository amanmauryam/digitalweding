from django.urls import path

from . import views

app_name = "websites"

# The owner routes live under ``/sites/`` so they never clash with the
# invitation builder routes (``/dashboard/``, ``/w/<slug>/``).
urlpatterns = [
    # --- owner ------------------------------------------------------------
    path("sites/dashboard/", views.dashboard, name="dashboard"),
    path("sites/dashboard/new/", views.create, name="create"),
    path("sites/dashboard/<slug:slug>/review/", views.review, name="review"),
    path("sites/dashboard/<slug:slug>/theme/", views.choose_theme, name="themes"),
    path("sites/dashboard/<slug:slug>/events/", views.events, name="events"),
    path("sites/dashboard/<slug:slug>/photos/", views.photos, name="photos"),
    path(
        "sites/dashboard/<slug:slug>/photos/<int:photo_id>/delete/",
        views.photo_delete,
        name="photo_delete",
    ),
    path("sites/dashboard/<slug:slug>/customize/", views.customize, name="customize"),
    path("sites/dashboard/<slug:slug>/preview/", views.preview, name="preview"),
    path(
        "sites/dashboard/<slug:slug>/preview/frame/",
        views.preview_frame,
        name="preview_frame",
    ),
    path("sites/dashboard/<slug:slug>/publish/", views.publish, name="publish"),
    path("sites/dashboard/<slug:slug>/unpublish/", views.unpublish, name="unpublish"),
    path("sites/dashboard/<slug:slug>/share/", views.share, name="share"),
    path("sites/dashboard/<slug:slug>/delete/", views.delete, name="delete"),
    path(
        "sites/dashboard/<slug:slug>/invitation/",
        views.invitation_source,
        name="invitation_source",
    ),
    path("sites/dashboard/<slug:slug>/rsvps/", views.rsvps, name="rsvps"),
    path("sites/dashboard/<slug:slug>/rsvps.csv", views.rsvps_csv, name="rsvps_csv"),
    path(
        "sites/dashboard/<slug:slug>/rsvps/<int:rsvp_id>/delete/",
        views.rsvp_delete,
        name="rsvp_delete",
    ),
    # --- public -----------------------------------------------------------
    path("wedding/<slug:slug>/", views.public_site, name="public_site"),
    path("wedding/<slug:slug>/rsvp/", views.public_rsvp, name="public_rsvp"),
]
