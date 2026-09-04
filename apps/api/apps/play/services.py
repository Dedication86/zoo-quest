"""
Game logic for the scan loop (Blueprint, Section A "Where the game logic lives").

`resolve_scan` is the referee: given a session and a marker code it decides
what happened, records it, awards XP, and returns everything the Success
screen needs in one object. Challenge completion (M3) and badge rules (M4)
plug into the marked spots.
"""

from dataclasses import dataclass, field

from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.content.models import Marker, Quest

from .models import Discovery, GuestSession, Scan, XPEvent


class ScanError(Exception):
    def __init__(self, code, message, status=400):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status = status


@dataclass
class ScanResult:
    marker: Marker
    result: str = ""  # Scan.Result value
    discovery_xp: int = 0
    completed_challenges: list = field(default_factory=list)  # M3
    unlocked_badges: list = field(default_factory=list)  # M4
    level_up: object = None
    total_xp: int = 0
    suggested_quest: Quest | None = None

    @property
    def is_new(self):
        return self.result == Scan.Result.DISCOVERY


def create_session(zoo, team_name="", user_agent=""):
    return GuestSession.objects.create(zoo=zoo, team_name=team_name[:40], user_agent=user_agent[:200])


def resolve_scan(session: GuestSession, code: str) -> ScanResult:
    code = (code or "").strip().upper()
    marker = (
        Marker.objects.select_related("zoo", "exhibit", "animal", "animal__exhibit").filter(code=code).first()
    )
    if marker is None:
        raise ScanError("unknown_marker", "That marker isn't part of any quest. Try another one.", 404)
    if marker.zoo_id != session.zoo_id:
        raise ScanError("wrong_zoo", f"That marker belongs to {marker.zoo.name}, not your zoo.", 400)
    if not marker.is_active:
        raise ScanError("inactive_marker", "That marker is retired. Look for a newer sign nearby.", 410)

    result = ScanResult(marker=marker, total_xp=session.total_xp)

    with transaction.atomic():
        if marker.animal_id is None:
            result.result = Scan.Result.EXHIBIT
        else:
            try:
                with transaction.atomic():
                    Discovery.objects.create(session=session, animal=marker.animal, marker=marker)
                is_new = True
            except IntegrityError:
                is_new = False
            if is_new:
                result.result = Scan.Result.DISCOVERY
                result.discovery_xp = int(session.zoo.setting("discovery_xp", 0))
                result.total_xp, result.level_up = session.add_xp(
                    result.discovery_xp, XPEvent.Source.DISCOVERY, marker.animal_id
                )
            else:
                result.result = Scan.Result.REPEAT

        Scan.objects.create(
            session=session, marker=marker, result=result.result, xp_awarded=result.discovery_xp
        )

        # M3 hook: complete any active-quest challenge that accepts this marker.
        # M4 hook: evaluate badge rules after XP changes.

    result.suggested_quest = suggest_quest_for(marker)
    return result


def suggest_quest_for(marker):
    """The first live quest that includes a challenge this marker completes."""
    now = timezone.now()
    return (
        Quest.objects.for_zoo(marker.zoo)
        .active()
        .filter(steps__challenge__accept_markers=marker)
        .exclude(starts_at__gt=now)
        .exclude(ends_at__lt=now)
        .order_by("-is_featured", "sort_order")
        .first()
    )


def profile_for(session: GuestSession) -> dict:
    discoveries = session.discoveries.select_related("animal", "animal__exhibit").order_by("discovered_at")
    return {
        "token": str(session.token),
        "zoo": {"slug": session.zoo.slug, "name": session.zoo.name},
        "team_name": session.team_name,
        "total_xp": session.total_xp,
        "level": session.level_info(),
        "stats": {
            "animals_discovered": discoveries.count(),
            "animals_total": session.zoo.animals.filter(is_active=True).count(),
            "scans": session.scans.count(),
            "challenges_completed": session.attempts.filter(status="completed").count(),
            "badges": 0,  # M4
        },
        "discoveries": [
            {
                "slug": d.animal.slug,
                "name": d.animal.name,
                "emoji": d.animal.emoji,
                "image": d.animal.image.url if d.animal.image else None,
                "exhibit": d.animal.exhibit.name,
                "discovered_at": d.discovered_at,
            }
            for d in discoveries
        ],
        "created_at": session.created_at,
    }
