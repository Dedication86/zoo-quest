from rest_framework import serializers

from apps.content.serializers import AnimalDetailSerializer, QuestListSerializer


class CreateSessionSerializer(serializers.Serializer):
    team_name = serializers.CharField(max_length=40, required=False, allow_blank=True, default="")


class UpdateSessionSerializer(serializers.Serializer):
    team_name = serializers.CharField(max_length=40, allow_blank=True)


class ScanRequestSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=40)


class ScanResponseSerializer(serializers.Serializer):
    """Documented shape of POST /scan (Blueprint, Section E)."""

    marker = serializers.DictField()
    animal = AnimalDetailSerializer(allow_null=True)
    discovery = serializers.DictField()
    completed_challenges = serializers.ListField()
    unlocked_badges = serializers.ListField()
    level_up = serializers.DictField(allow_null=True)
    totals = serializers.DictField()
    suggested_quest = QuestListSerializer(allow_null=True)
