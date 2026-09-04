"""
Tenant layer. A Zoo is the unit of multi-tenancy: every content and play row
belongs to exactly one Zoo (Blueprint, Section D). Shared database, row-level
scoping. No schema-per-tenant machinery in the MVP.
"""

from django.conf import settings
from django.db import models


class Zoo(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, help_text="Used in URLs: /z/<slug>")
    timezone = models.CharField(max_length=64, default="UTC")
    logo = models.ImageField(upload_to="zoos/logos/", blank=True)
    map_image = models.ImageField(
        upload_to="zoos/maps/", blank=True, help_text="Static map image that exhibit pins are placed on."
    )
    primary_color = models.CharField(max_length=7, default="#2F6B4F")
    settings = models.JSONField(
        default=dict,
        blank=True,
        help_text="discovery_xp, quest_complete_xp, xp_by_difficulty, repeat_scan_cooldown_minutes",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    # ---- game settings -------------------------------------------------
    def setting(self, key, default=None):
        """Per-zoo override, falling back to ZOOQUEST_DEFAULTS. Never hardcode a game number."""
        if key in self.settings:
            return self.settings[key]
        return settings.ZOOQUEST_DEFAULTS.get(key, default)

    def xp_for_difficulty(self, difficulty):
        table = self.setting("xp_by_difficulty", {})
        return int(table.get(difficulty, 0))


class StaffMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        EDITOR = "editor", "Editor"
        VIEWER = "viewer", "Viewer"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="zoo_memberships"
    )
    zoo = models.ForeignKey(Zoo, on_delete=models.CASCADE, related_name="memberships")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.EDITOR)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "zoo")]

    def __str__(self):
        return f"{self.user} @ {self.zoo} ({self.role})"


class ZooScopedQuerySet(models.QuerySet):
    def for_zoo(self, zoo):
        return self.filter(zoo=zoo)

    def active(self):
        return self.filter(is_active=True)


class ZooScopedModel(models.Model):
    """
    Abstract base for everything a zoo owns. Adds the tenant FK and an
    `objects.for_zoo(zoo)` manager. Content and play models inherit this.
    """

    zoo = models.ForeignKey(Zoo, on_delete=models.CASCADE, related_name="%(class)ss")
    objects = ZooScopedQuerySet.as_manager()

    class Meta:
        abstract = True


def zoos_for_user(user):
    """Zoos this user may administer. Superusers see all."""
    if user.is_superuser:
        return Zoo.objects.all()
    return Zoo.objects.filter(memberships__user=user)
