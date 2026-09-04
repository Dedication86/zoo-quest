"""
Guest identity. The explorer app sends `X-Guest-Token: <uuid>`; we resolve it
to a GuestSession and expose it as request.guest. No Django User is involved.
"""

import uuid

from drf_spectacular.extensions import OpenApiAuthenticationExtension
from rest_framework import authentication, exceptions, permissions

from .models import GuestSession

HEADER = "HTTP_X_GUEST_TOKEN"


class GuestUser:
    """Minimal stand-in so DRF's request.user machinery is satisfied."""

    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, session):
        self.session = session
        self.pk = session.pk  # DRF throttling keys on user.pk

    def __str__(self):
        return f"guest:{self.session.pk}"


class GuestTokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        raw = request.META.get(HEADER)
        if not raw:
            return None
        try:
            token = uuid.UUID(raw.strip())
        except ValueError:
            raise exceptions.AuthenticationFailed("That explorer token is not valid.") from None
        session = GuestSession.objects.select_related("zoo").filter(token=token, zoo__is_active=True).first()
        if session is None:
            raise exceptions.AuthenticationFailed("We could not find your adventure. Start a new one.")
        session.save(update_fields=["last_seen_at"])  # heartbeat for session-length analytics
        request.guest = session
        return (GuestUser(session), token)

    def authenticate_header(self, request):
        return "X-Guest-Token"


class IsGuest(permissions.BasePermission):
    message = "Start an adventure first."

    def has_permission(self, request, view):
        return getattr(request, "guest", None) is not None


class GuestTokenScheme(OpenApiAuthenticationExtension):
    """Tells drf-spectacular (and the generated TypeScript client) about the header."""

    target_class = "apps.play.auth.GuestTokenAuthentication"
    name = "guestToken"

    def get_security_definition(self, auto_schema):
        return {"type": "apiKey", "in": "header", "name": "X-Guest-Token"}
