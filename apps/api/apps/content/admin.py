"""
Django Admin is the MVP admin dashboard (Blueprint, Section G).
Everything here is zoo-scoped through ZooScopedAdmin.
"""

from django import forms
from django.contrib import admin, messages
from django.shortcuts import render
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import action

from apps.tenants.admin import ZooScopedAdmin

from .challenge_types import CHALLENGE_TYPES, get_type
from .models import Animal, Badge, Challenge, Exhibit, Level, Marker, Quest, QuestChallenge
from .qr import marker_url, qr_data_uri

# ----------------------------------------------------------------------------- inlines


class AnimalInline(TabularInline):
    model = Animal
    fields = ["name", "species", "emoji", "conservation_status", "is_active"]
    extra = 0
    show_change_link = True


class MarkerInline(TabularInline):
    model = Marker
    fields = ["code", "animal", "label", "is_active"]
    extra = 0
    show_change_link = True


class QuestChallengeInline(TabularInline):
    model = QuestChallenge
    fields = ["order", "challenge", "is_final"]
    extra = 0
    ordering_field = "order"
    autocomplete_fields = ["challenge"]


# ----------------------------------------------------------------------------- exhibits & animals


@admin.register(Exhibit)
class ExhibitAdmin(ZooScopedAdmin):
    list_display = [
        "name",
        "zoo",
        "animal_count",
        "marker_count",
        "map_x",
        "map_y",
        "sort_order",
        "is_active",
    ]
    list_filter = ["zoo", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [AnimalInline, MarkerInline]
    fieldsets = (
        (None, {"fields": ("zoo", "name", "slug", "description", "image", "sort_order", "is_active")}),
        (
            "Map pin",
            {"fields": (("map_x", "map_y"),), "description": "Percent from the left / top of the zoo map."},
        ),
    )

    @admin.display(description="Animals")
    def animal_count(self, obj):
        return obj.animals.count()

    @admin.display(description="Markers")
    def marker_count(self, obj):
        return obj.markers.count()


@admin.register(Animal)
class AnimalAdmin(ZooScopedAdmin):
    list_display = ["icon", "name", "species", "exhibit", "conservation_status", "tag_list", "is_active"]
    list_display_links = ["icon", "name"]
    list_filter = ["zoo", "exhibit", "conservation_status", "is_active"]
    search_fields = ["name", "species", "scientific_name", "tags"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [MarkerInline]
    fieldsets = (
        (None, {"fields": ("zoo", "exhibit", "name", "slug", "emoji", "image", "is_active")}),
        ("About", {"fields": ("species", "scientific_name", "description", "fun_facts", "tags")}),
        ("Conservation", {"fields": ("conservation_status", "conservation_info")}),
    )

    @admin.display(description="")
    def icon(self, obj):
        return obj.emoji or "•"

    @admin.display(description="Tags")
    def tag_list(self, obj):
        return ", ".join(obj.tags or [])


# ----------------------------------------------------------------------------- markers (QR)


@admin.register(Marker)
class MarkerAdmin(ZooScopedAdmin):
    list_display = ["qr_preview", "code", "label", "exhibit", "animal", "is_active"]
    list_display_links = ["code"]
    list_filter = ["zoo", "exhibit", "is_active"]
    search_fields = ["code", "label"]
    readonly_fields = ["qr_large", "scan_url"]
    actions = ["print_qr_sheet"]
    fieldsets = (
        (None, {"fields": ("zoo", "exhibit", "animal", "label", "code", "is_active")}),
        ("QR code", {"fields": ("scan_url", "qr_large")}),
    )

    @admin.display(description="QR")
    def qr_preview(self, obj):
        return format_html(
            '<img src="{}" width="44" height="44" alt="QR">', qr_data_uri(marker_url(obj), box_size=2)
        )

    @admin.display(description="Preview")
    def qr_large(self, obj):
        if not obj.pk:
            return "Save first to generate the QR code."
        return format_html(
            '<img src="{}" width="220" height="220" alt="QR">', qr_data_uri(marker_url(obj), 6)
        )

    @admin.display(description="Scan URL")
    def scan_url(self, obj):
        return marker_url(obj) if obj.pk else "—"

    @action(description="Print QR sheet for selected markers")
    def print_qr_sheet(self, request, queryset):
        markers = queryset.select_related("exhibit", "animal", "zoo").order_by("exhibit__sort_order", "code")
        cards = [
            {
                "marker": m,
                "url": marker_url(m),
                "qr": qr_data_uri(marker_url(m), box_size=8),
                "title": m.animal.name if m.animal else m.exhibit.name,
                "emoji": (m.animal.emoji if m.animal else "") or "",
            }
            for m in markers
        ]
        if not cards:
            self.message_user(request, "Select at least one marker.", level=messages.WARNING)
            return None
        return render(request, "content/qr_sheet.html", {"cards": cards, "zoo": markers[0].zoo})


# ----------------------------------------------------------------------------- challenges


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        ctype = cleaned.get("challenge_type")
        if ctype:
            markers = cleaned.get("accept_markers")
            problems = get_type(ctype).validate_config(
                cleaned.get("config") or {}, len(markers) if markers else 0
            )
            for p in problems:
                self.add_error("config" if "marker" not in p else "accept_markers", p)
        return cleaned


@admin.register(Challenge)
class ChallengeAdmin(ZooScopedAdmin):
    form = ChallengeForm
    list_display = [
        "title",
        "challenge_type",
        "difficulty",
        "xp_reward",
        "animal",
        "exhibit",
        "in_quests",
        "is_active",
    ]
    list_filter = ["zoo", "challenge_type", "difficulty", "is_active", "quests"]
    search_fields = ["title", "prompt", "slug"]
    prepopulated_fields = {"slug": ["title"]}
    autocomplete_fields = ["animal", "exhibit"]
    filter_horizontal = ["accept_markers"]
    readonly_fields = ["type_help"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "zoo",
                    "title",
                    "slug",
                    "challenge_type",
                    "type_help",
                    "difficulty",
                    "xp_reward",
                    "is_active",
                )
            },
        ),
        ("What the family sees", {"fields": ("prompt", "hint", "explanation")}),
        ("Where it happens", {"fields": ("animal", "exhibit", "accept_markers")}),
        (
            "Answer configuration",
            {
                "fields": ("config",),
                "description": 'Who Am I / Conservation: {"options": ["A","B","C"], "correct": "A"}. '
                'Observation: {"timer_seconds": 30, "options": ["Eating","Resting"]}. '
                'Photo: {"verification": "self_report"}. Hunts: leave empty and pick accepted markers.',
            },
        ),
    )

    @admin.display(description="Type guide")
    def type_help(self, obj):
        rows = "".join(
            f"<li><b>{t.label}</b>: {t.description}"
            + (f" <code>config: {', '.join(t.config_keys)}</code>" if t.config_keys else "")
            + "</li>"
            for t in CHALLENGE_TYPES.values()
        )
        return format_html('<ul style="margin:0;padding-left:1.2em">{}</ul>', format_html(rows))

    @admin.display(description="Quests")
    def in_quests(self, obj):
        return ", ".join(q.name for q in obj.quests.all()) or "—"


# ----------------------------------------------------------------------------- quests, badges, levels


@admin.register(Quest)
class QuestAdmin(ZooScopedAdmin):
    list_display = [
        "name",
        "zoo",
        "step_count",
        "xp_reward",
        "badge",
        "estimated_minutes",
        "is_featured",
        "is_active",
    ]
    list_filter = ["zoo", "is_featured", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}
    inlines = [QuestChallengeInline]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "zoo",
                    "name",
                    "slug",
                    "description",
                    "cover_image",
                    "is_featured",
                    "sort_order",
                    "is_active",
                )
            },
        ),
        ("Reward", {"fields": ("xp_reward", "badge", "estimated_minutes")}),
        ("Schedule (seasonal quests)", {"fields": ("starts_at", "ends_at"), "classes": ["collapse"]}),
    )

    @admin.display(description="Missions")
    def step_count(self, obj):
        return obj.steps.count()


@admin.register(Badge)
class BadgeAdmin(ZooScopedAdmin):
    list_display = ["icon", "name", "rule_preview", "xp_reward", "is_secret", "is_active"]
    list_display_links = ["icon", "name"]
    list_filter = ["zoo", "rule_type", "is_secret", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ["name"]}
    readonly_fields = ["rule_preview"]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "zoo",
                    "name",
                    "slug",
                    "description",
                    "icon",
                    "image",
                    "xp_reward",
                    "is_secret",
                    "is_active",
                )
            },
        ),
        (
            "Rule",
            {
                "fields": ("rule_type", "rule_config", "rule_preview"),
                "description": 'Examples: {"count": 5}, {"count": 2, "tag": "reptile"}, '
                '{"animal_slugs": ["giraffe"]}, {"challenge_type": "conservation", "count": 3}, '
                '{"quest_slug": "savanna-safari"}',
            },
        ),
    )

    @admin.display(description="Earned when")
    def rule_preview(self, obj):
        return obj.rule_sentence() if obj.pk else "—"


@admin.register(Level)
class LevelAdmin(ZooScopedAdmin):
    list_display = ["number", "title", "xp_required", "zoo"]
    list_filter = ["zoo"]
    list_editable = ["title", "xp_required"]
    ordering = ["zoo", "number"]


# Quest steps are edited inline on the Quest page; keep them out of the sidebar.
class _HiddenModelAdmin(ModelAdmin):
    def has_module_permission(self, request):
        return False


admin.site.register(QuestChallenge, _HiddenModelAdmin)
