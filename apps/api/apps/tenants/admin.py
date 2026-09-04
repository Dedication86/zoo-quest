from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline

from .models import StaffMembership, Zoo, zoos_for_user


class ZooScopedAdmin(ModelAdmin):
    """
    Base admin for anything with a `zoo` FK. Staff only see rows for zoos they
    belong to; superusers see everything. When a user belongs to exactly one
    zoo, the zoo field is filled in for them.
    """

    zoo_field = "zoo"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(**{f"{self.zoo_field}__in": zoos_for_user(request.user)})

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if not request.user.is_superuser:
            related = db_field.related_model
            if related is Zoo:
                kwargs["queryset"] = zoos_for_user(request.user)
            elif hasattr(related, "zoo"):
                kwargs["queryset"] = related.objects.filter(zoo__in=zoos_for_user(request.user))
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        related = db_field.related_model
        if not request.user.is_superuser and hasattr(related, "zoo"):
            kwargs["queryset"] = related.objects.filter(zoo__in=zoos_for_user(request.user))
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        zoos = zoos_for_user(request.user)
        if zoos.count() == 1 and self.zoo_field == "zoo":
            initial.setdefault("zoo", zoos.first().pk)
        return initial


class StaffInline(TabularInline):
    model = StaffMembership
    extra = 0
    autocomplete_fields = ["user"]


@admin.register(Zoo)
class ZooAdmin(ModelAdmin):
    list_display = ["name", "slug", "timezone", "is_active", "created_at"]
    prepopulated_fields = {"slug": ["name"]}
    search_fields = ["name", "slug"]
    inlines = [StaffInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "timezone", "is_active")}),
        ("Branding", {"fields": ("logo", "map_image", "primary_color")}),
        (
            "Game settings",
            {
                "fields": ("settings",),
                "description": "JSON overrides: discovery_xp, quest_complete_xp, "
                'xp_by_difficulty {"easy":50,"medium":100,"hard":250}, repeat_scan_cooldown_minutes.',
            },
        ),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs if request.user.is_superuser else qs.filter(pk__in=zoos_for_user(request.user))


@admin.register(StaffMembership)
class StaffMembershipAdmin(ZooScopedAdmin):
    list_display = ["user", "zoo", "role", "created_at"]
    list_filter = ["role", "zoo"]
    autocomplete_fields = ["user"]
