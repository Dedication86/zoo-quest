"""
Read-only content endpoints (Blueprint, Section E). All are zoo-scoped by slug.
Per-session state (discovered, completed) is layered on in M2; these views
describe the zoo as it is, independent of who is asking.
"""

from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.tenants.models import Zoo

from .models import Animal, Exhibit, Level, Marker, Quest, QuestChallenge
from .serializers import (
    AnimalCardSerializer,
    AnimalDetailSerializer,
    ExhibitSerializer,
    LevelSerializer,
    MarkerSerializer,
    QuestDetailSerializer,
    QuestListSerializer,
)


def get_zoo(slug):
    return get_object_or_404(Zoo, slug=slug, is_active=True)


def live_quests(zoo):
    """Active quests whose schedule (if any) includes now."""
    now = timezone.now()
    return (
        Quest.objects.for_zoo(zoo)
        .active()
        .filter(Q(starts_at__isnull=True) | Q(starts_at__lte=now))
        .filter(Q(ends_at__isnull=True) | Q(ends_at__gte=now))
        .annotate(mission_count=Count("steps"))
        .select_related("badge")
    )


class ZooSummaryView(APIView):
    """GET /zoos/{zoo}/ — what the Welcome screen needs."""

    @extend_schema(responses={200: dict}, tags=["content"])
    def get(self, request, zoo_slug):
        zoo = get_zoo(zoo_slug)
        return Response(
            {
                "slug": zoo.slug,
                "name": zoo.name,
                "logo": zoo.logo.url if zoo.logo else None,
                "primary_color": zoo.primary_color,
                "timezone": zoo.timezone,
                "quest_count": live_quests(zoo).count(),
                "animal_count": Animal.objects.for_zoo(zoo).active().count(),
                "levels": LevelSerializer(Level.objects.for_zoo(zoo), many=True).data,
            }
        )


class QuestListView(generics.ListAPIView):
    serializer_class = QuestListSerializer
    pagination_class = None

    def get_queryset(self):
        return live_quests(get_zoo(self.kwargs["zoo_slug"]))


class QuestDetailView(generics.RetrieveAPIView):
    serializer_class = QuestDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "quest_slug"

    def get_queryset(self):
        steps = Prefetch(
            "steps",
            queryset=QuestChallenge.objects.select_related(
                "challenge", "challenge__animal", "challenge__animal__exhibit", "challenge__exhibit"
            ).order_by("order"),
        )
        return live_quests(get_zoo(self.kwargs["zoo_slug"])).prefetch_related(steps)


class MapView(APIView):
    """GET /zoos/{zoo}/map/ — exhibits with pins and their animals."""

    @extend_schema(responses={200: dict}, tags=["content"])
    def get(self, request, zoo_slug):
        zoo = get_zoo(zoo_slug)
        exhibits = (
            Exhibit.objects.for_zoo(zoo)
            .active()
            .annotate(animal_count=Count("animals", filter=Q(animals__is_active=True)))
            .prefetch_related(Prefetch("animals", queryset=Animal.objects.active()))
        )
        payload = []
        for ex in exhibits:
            item = ExhibitSerializer(ex).data
            item["animals"] = AnimalCardSerializer(ex.animals.all(), many=True).data
            payload.append(item)
        return Response({"map_image": zoo.map_image.url if zoo.map_image else None, "exhibits": payload})


class AnimalListView(generics.ListAPIView):
    serializer_class = AnimalCardSerializer
    pagination_class = None

    def get_queryset(self):
        return Animal.objects.for_zoo(get_zoo(self.kwargs["zoo_slug"])).active().select_related("exhibit")


class AnimalDetailView(generics.RetrieveAPIView):
    serializer_class = AnimalDetailSerializer
    lookup_field = "slug"
    lookup_url_kwarg = "animal_slug"

    def get_queryset(self):
        return Animal.objects.for_zoo(get_zoo(self.kwargs["zoo_slug"])).active().select_related("exhibit")


class MarkerLookupView(APIView):
    """
    GET /markers/{code}/ — resolve a printed code to its zoo, exhibit and animal.
    The /s/[code] landing page uses this before a session exists. M2's POST /scan
    is the one that records anything.
    """

    @extend_schema(responses={200: MarkerSerializer}, tags=["content"])
    def get(self, request, code):
        marker = get_object_or_404(
            Marker.objects.select_related("zoo", "exhibit", "animal"), code=code.upper(), is_active=True
        )
        data = MarkerSerializer(marker).data
        data["zoo"] = {"slug": marker.zoo.slug, "name": marker.zoo.name}
        data["exhibit_name"] = marker.exhibit.name
        data["animal_name"] = marker.animal.name if marker.animal else None
        return Response(data)
