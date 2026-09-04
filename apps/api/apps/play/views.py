from django.db.models import Count
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.content.serializers import AnimalDetailSerializer, QuestListSerializer
from apps.tenants.models import Zoo

from .auth import IsGuest
from .serializers import (
    CreateSessionSerializer,
    ScanRequestSerializer,
    ScanResponseSerializer,
    UpdateSessionSerializer,
)
from .services import ScanError, create_session, profile_for, resolve_scan


class SessionCreateView(APIView):
    """POST /zoos/{zoo}/sessions/ — start an anonymous adventure. Returns the token to keep."""

    authentication_classes = []
    permission_classes = []

    @extend_schema(request=CreateSessionSerializer, responses={201: dict}, tags=["play"])
    def post(self, request, zoo_slug):
        zoo = get_object_or_404(Zoo, slug=zoo_slug, is_active=True)
        data = CreateSessionSerializer(data=request.data or {})
        data.is_valid(raise_exception=True)
        session = create_session(
            zoo,
            team_name=data.validated_data["team_name"],
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
        )
        return Response(profile_for(session), status=status.HTTP_201_CREATED)


class MeView(APIView):
    """GET /me/ — the explorer profile. PATCH /me/ — change the team name."""

    permission_classes = [IsGuest]

    @extend_schema(responses={200: dict}, tags=["play"])
    def get(self, request):
        return Response(profile_for(request.guest))

    @extend_schema(request=UpdateSessionSerializer, responses={200: dict}, tags=["play"])
    def patch(self, request):
        data = UpdateSessionSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        request.guest.team_name = data.validated_data["team_name"].strip()
        request.guest.save(update_fields=["team_name"])
        return Response(profile_for(request.guest))


class ScanView(APIView):
    """POST /scan/ {code} — the main verb. One response renders the Success screen."""

    permission_classes = [IsGuest]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "scan"

    @extend_schema(request=ScanRequestSerializer, responses={200: ScanResponseSerializer}, tags=["play"])
    def post(self, request):
        data = ScanRequestSerializer(data=request.data)
        data.is_valid(raise_exception=True)
        try:
            r = resolve_scan(request.guest, data.validated_data["code"])
        except ScanError as e:
            return Response({"error": e.code, "detail": e.message}, status=e.status)

        session = request.guest
        m = r.marker
        payload = {
            "marker": {
                "code": m.code,
                "label": m.label,
                "exhibit": {"slug": m.exhibit.slug, "name": m.exhibit.name},
            },
            "animal": AnimalDetailSerializer(m.animal).data if m.animal else None,
            "discovery": {"result": r.result, "is_new": r.is_new, "xp": r.discovery_xp},
            "completed_challenges": r.completed_challenges,
            "unlocked_badges": r.unlocked_badges,
            "level_up": (
                {
                    "number": r.level_up.number,
                    "title": r.level_up.title,
                    "xp_required": r.level_up.xp_required,
                }
                if r.level_up
                else None
            ),
            "totals": {"xp": r.total_xp, "level": session.level_info()},
            "suggested_quest": QuestListSerializer(_with_mission_count(r.suggested_quest)).data
            if r.suggested_quest
            else None,
        }
        return Response(payload)


def _with_mission_count(quest):
    return type(quest).objects.filter(pk=quest.pk).annotate(mission_count=Count("steps")).first()
