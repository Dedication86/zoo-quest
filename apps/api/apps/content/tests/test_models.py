import pytest
from django.core.exceptions import ValidationError

from apps.content.models import Badge, Challenge, Exhibit, Level, Marker


@pytest.mark.django_db
class TestFixture:
    def test_cedar_hollow_loads_completely(self, cedar_hollow):
        z = cedar_hollow
        assert z.exhibits.count() == 5
        assert z.animals.count() == 10
        assert z.markers.count() == 11
        assert z.challenges.count() == 20
        assert z.quests.count() == 3
        assert z.badges.count() == 8
        assert z.levels.count() == 5

    def test_every_challenge_config_is_valid(self, cedar_hollow):
        for c in Challenge.objects.all():
            assert c.validate_config() == [], c.slug

    def test_every_quest_has_exactly_one_final_step(self, cedar_hollow):
        for q in cedar_hollow.quests.all():
            finals = q.steps.filter(is_final=True)
            assert finals.count() == 1, q.slug
            assert finals.first().order == q.steps.count()


@pytest.mark.django_db
class TestGameRules:
    def test_zoo_settings_fall_back_to_defaults(self, cedar_hollow):
        cedar_hollow.settings = {}
        assert cedar_hollow.setting("discovery_xp") == 100
        assert cedar_hollow.xp_for_difficulty("hard") == 250
        cedar_hollow.settings = {"discovery_xp": 42}
        assert cedar_hollow.setting("discovery_xp") == 42

    def test_challenge_xp_defaults_from_difficulty(self, cedar_hollow):
        c = Challenge.objects.create(
            zoo=cedar_hollow, title="Temp", challenge_type="photo", difficulty="hard", prompt="x"
        )
        assert c.xp_reward == 250
        assert c.slug == "temp"

    def test_level_for_xp(self, cedar_hollow):
        current, nxt = Level.for_xp(cedar_hollow, 0)
        assert (current.number, nxt.number) == (1, 2)
        current, nxt = Level.for_xp(cedar_hollow, 1400)
        assert (current.number, nxt.number) == (3, 4)
        current, nxt = Level.for_xp(cedar_hollow, 99_999)
        assert current.number == 5 and nxt is None

    def test_public_config_never_leaks_answer(self, cedar_hollow):
        c = Challenge.objects.get(slug="who-elephant")
        assert "correct" in c.config
        assert "correct" not in c.public_config()
        assert c.public_config()["options"] == c.config["options"]

    def test_marker_code_generation_is_unique_per_subject(self, cedar_hollow):
        wild_north = Exhibit.objects.get(slug="wild-north")
        m1 = Marker.objects.create(zoo=cedar_hollow, exhibit=wild_north, label="a")
        m2 = Marker.objects.create(zoo=cedar_hollow, exhibit=wild_north, label="b")
        assert m1.code == "CHZ-WILDNORTH-001"
        assert m2.code == "CHZ-WILDNORTH-002"

    def test_who_am_i_rejects_answer_not_in_options(self, cedar_hollow):
        c = Challenge(
            zoo=cedar_hollow,
            title="Bad",
            challenge_type="who_am_i",
            prompt="?",
            config={"options": ["A", "B"], "correct": "C"},
        )
        with pytest.raises(ValidationError):
            c.full_clean()

    def test_badge_rule_sentences(self, cedar_hollow):
        sentences = {b.slug: b.rule_sentence() for b in Badge.objects.all()}
        assert sentences["reptile-ranger"] == "Discover 2 animal(s) tagged 'reptile'"
        assert sentences["savanna-scout"] == "Complete quest 'savanna-safari'"
