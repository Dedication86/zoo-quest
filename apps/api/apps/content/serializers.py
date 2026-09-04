"""
Public serializers. Rule: never send the browser something it should not know.
`Challenge.public_config()` strips the correct answer; hints are fetched
separately in M3 so revealing one can be logged.
"""

from rest_framework import serializers

from .models import Animal, Badge, Challenge, Exhibit, Level, Marker, Quest, QuestChallenge


class ExhibitSerializer(serializers.ModelSerializer):
    animal_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Exhibit
        fields = ["id", "slug", "name", "description", "image", "map_x", "map_y", "animal_count"]


class AnimalCardSerializer(serializers.ModelSerializer):
    """Compact: for lists and challenge references."""

    exhibit = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Animal
        fields = ["id", "slug", "name", "emoji", "image", "exhibit", "conservation_status"]


class AnimalDetailSerializer(AnimalCardSerializer):
    exhibit_name = serializers.CharField(source="exhibit.name", read_only=True)
    conservation_status_label = serializers.CharField(
        source="get_conservation_status_display", read_only=True
    )

    class Meta(AnimalCardSerializer.Meta):
        fields = AnimalCardSerializer.Meta.fields + [
            "species",
            "scientific_name",
            "description",
            "fun_facts",
            "conservation_status_label",
            "conservation_info",
            "tags",
            "exhibit_name",
        ]


class MarkerSerializer(serializers.ModelSerializer):
    exhibit = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    animal = serializers.SlugRelatedField(slug_field="slug", read_only=True)

    class Meta:
        model = Marker
        fields = ["code", "exhibit", "animal", "label"]


class ChallengeSerializer(serializers.ModelSerializer):
    type = serializers.CharField(source="challenge_type")
    type_label = serializers.CharField(source="get_challenge_type_display", read_only=True)
    animal = AnimalCardSerializer(read_only=True)
    exhibit = serializers.SlugRelatedField(slug_field="slug", read_only=True)
    has_hint = serializers.SerializerMethodField()
    config = serializers.SerializerMethodField()

    class Meta:
        model = Challenge
        fields = [
            "id",
            "slug",
            "title",
            "type",
            "type_label",
            "difficulty",
            "xp_reward",
            "prompt",
            "has_hint",
            "animal",
            "exhibit",
            "config",
        ]

    def get_has_hint(self, obj) -> bool:
        return bool(obj.hint)

    def get_config(self, obj) -> dict:
        return obj.public_config()


class BadgeSerializer(serializers.ModelSerializer):
    requirement = serializers.CharField(source="rule_sentence", read_only=True)

    class Meta:
        model = Badge
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "icon",
            "image",
            "xp_reward",
            "is_secret",
            "requirement",
        ]


class QuestStepSerializer(serializers.ModelSerializer):
    challenge = ChallengeSerializer(read_only=True)

    class Meta:
        model = QuestChallenge
        fields = ["order", "is_final", "challenge"]


class QuestListSerializer(serializers.ModelSerializer):
    badge = BadgeSerializer(read_only=True)
    mission_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Quest
        fields = [
            "id",
            "slug",
            "name",
            "description",
            "cover_image",
            "xp_reward",
            "badge",
            "estimated_minutes",
            "is_featured",
            "mission_count",
        ]


class QuestDetailSerializer(QuestListSerializer):
    steps = QuestStepSerializer(many=True, read_only=True)

    class Meta(QuestListSerializer.Meta):
        fields = QuestListSerializer.Meta.fields + ["steps"]


class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ["number", "title", "xp_required"]
