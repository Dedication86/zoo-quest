"""Read-mostly views of play data for debugging and support. Analytics proper arrives in M5."""

from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from apps.tenants.admin import ZooScopedAdmin

from .models import Discovery, GuestSession, Scan, XPEvent


class DiscoveryInline(TabularInline):
    model = Discovery
    fields = ["animal", "marker", "discovered_at"]
    readonly_fields = fields
    extra = 0
    can_delete = False


class XPEventInline(TabularInline):
    model = XPEvent
    fields = ["amount", "source_type", "source_id", "created_at"]
    readonly_fields = fields
    extra = 0
    can_delete = False


@admin.register(GuestSession)
class GuestSessionAdmin(ZooScopedAdmin):
    list_display = [
        "__str__",
        "zoo",
        "total_xp",
        "discovery_count",
        "scan_count",
        "created_at",
        "last_seen_at",
    ]
    list_filter = ["zoo", "created_at"]
    search_fields = ["team_name", "token"]
    readonly_fields = ["token", "total_xp", "created_at", "last_seen_at", "user_agent"]
    inlines = [DiscoveryInline, XPEventInline]
    date_hierarchy = "created_at"

    @admin.display(description="Discovered")
    def discovery_count(self, obj):
        return obj.discoveries.count()

    @admin.display(description="Scans")
    def scan_count(self, obj):
        return obj.scans.count()


@admin.register(Scan)
class ScanAdmin(ModelAdmin):
    list_display = ["scanned_at", "session", "marker", "result", "xp_awarded"]
    list_filter = ["result", "marker__zoo", "marker__exhibit"]
    readonly_fields = ["session", "marker", "result", "xp_awarded", "scanned_at"]
    date_hierarchy = "scanned_at"

    def has_add_permission(self, request):
        return False
