"""
Play: what a family does. One GuestSession is one family sharing one phone
(Blueprint, Section 0 decision 5). Everything here is write-heavy, per-session,
and anonymous: no names, no emails, no device IDs beyond a random token.
"""

import uuid

from django.db import models, transaction
from django.db.models import F

from apps.content.models import Animal, Challenge, Level, Marker, Quest
from apps.tenants.models import ZooScopedModel


class GuestSession(ZooScopedModel):
    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    team_name = models.CharField(max_length=40, blank=True)
    total_xp = models.PositiveIntegerField(default=0)  # denormalized from XPEvent
    created_at = models.DateTimeField(auto_now_add=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    user_agent = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.team_name or f"Explorer {str(self.token)[:8]}"

    # ---- progression -----------------------------------------------------
    def level_info(self):
        current, nxt = Level.for_xp(self.zoo, self.total_xp)
        return {
            "number": current.number if current else 1,
            "title": current.title if current else "Explorer",
            "xp_required": current.xp_required if current else 0,
            "next_title": nxt.title if nxt else None,
            "next_at": nxt.xp_required if nxt else None,
        }

    def add_xp(self, amount, source_type, source_id=None):
        """
        Append to the ledger and bump the denormalized total atomically.
        Returns (new_total, level_up) where level_up is the new Level or None.
        """
        if amount <= 0:
            return self.total_xp, None
        before, _ = Level.for_xp(self.zoo, self.total_xp)
        with transaction.atomic():
            XPEvent.objects.create(session=self, amount=amount, source_type=source_type, source_id=source_id)
            GuestSession.objects.filter(pk=self.pk).update(total_xp=F("total_xp") + amount)
            self.refresh_from_db(fields=["total_xp"])
        after, _ = Level.for_xp(self.zoo, self.total_xp)
        level_up = after if after and (before is None or after.number > before.number) else None
        return self.total_xp, level_up


class Scan(models.Model):
    """Raw log: one row per scan, including repeats. Analytics reads this."""

    class Result(models.TextChoices):
        DISCOVERY = "discovery", "New discovery"
        REPEAT = "repeat", "Already discovered"
        EXHIBIT = "exhibit", "Exhibit marker (no animal)"

    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name="scans")
    marker = models.ForeignKey(Marker, on_delete=models.CASCADE, related_name="scans")
    result = models.CharField(max_length=12, choices=Result.choices)
    xp_awarded = models.PositiveIntegerField(default=0)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scanned_at"]


class Discovery(models.Model):
    """One per animal per session. The unique constraint IS the anti-farming rule."""

    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name="discoveries")
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name="discoveries")
    marker = models.ForeignKey(Marker, on_delete=models.SET_NULL, null=True, related_name="+")
    discovered_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("session", "animal")]
        ordering = ["discovered_at"]


class QuestProgress(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        ABANDONED = "abandoned", "Abandoned"

    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name="quest_progress")
    quest = models.ForeignKey(Quest, on_delete=models.CASCADE, related_name="progress")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.ACTIVE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("session", "quest")]


class ChallengeAttempt(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In progress"
        COMPLETED = "completed", "Completed"

    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name="attempts")
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, related_name="attempts")
    quest_progress = models.ForeignKey(
        QuestProgress, on_delete=models.SET_NULL, null=True, blank=True, related_name="attempts"
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.IN_PROGRESS)
    attempts = models.PositiveIntegerField(default=0)
    answer = models.JSONField(null=True, blank=True)
    xp_awarded = models.PositiveIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = [("session", "challenge")]


class XPEvent(models.Model):
    """Append-only ledger. Every XP change has a source."""

    class Source(models.TextChoices):
        DISCOVERY = "discovery", "Animal discovered"
        CHALLENGE = "challenge", "Challenge completed"
        QUEST = "quest", "Quest completed"
        BADGE = "badge", "Badge earned"
        ADJUSTMENT = "adjustment", "Manual adjustment"

    session = models.ForeignKey(GuestSession, on_delete=models.CASCADE, related_name="xp_events")
    amount = models.IntegerField()
    source_type = models.CharField(max_length=12, choices=Source.choices)
    source_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
