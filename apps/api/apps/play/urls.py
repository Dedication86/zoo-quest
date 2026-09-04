from django.urls import path

from . import views

urlpatterns = [
    path("zoos/<slug:zoo_slug>/sessions/", views.SessionCreateView.as_view(), name="session-create"),
    path("me/", views.MeView.as_view(), name="me"),
    path("scan/", views.ScanView.as_view(), name="scan"),
]
