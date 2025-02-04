from django.urls import path, include

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("contact/", views.contact, name="contact"),
    path("details/", views.details, name="details"),
    path("<str:mode>/", views.index_mode, name="index"),
    path("resources", views.resources, name="resources"),
    path("<str:mode>/event/<int:event_id>", views.event, name="event"),
    path("event/<int:event_id>", views.event, name="event"),
    path("<str:mode>/event_aspect/<int:event_id>/<int:aspect_id>", views.event_aspect, name="event_aspect"),
    path("event_aspect/<int:event_id>/<int:aspect_id>", views.event_aspect, name="event_aspect"),
]