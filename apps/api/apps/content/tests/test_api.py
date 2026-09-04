import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestContentApi:
    def test_zoo_summary(self, client, cedar_hollow):
        r = client.get(reverse("v1:zoo-summary", args=["cedar-hollow"]))
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "Cedar Hollow Zoo"
        assert body["quest_count"] == 3
        assert body["animal_count"] == 10
        assert [lvl["title"] for lvl in body["levels"]][0] == "Zoo Rookie"

    def test_unknown_zoo_is_404(self, client, cedar_hollow):
        assert client.get(reverse("v1:zoo-summary", args=["nope"])).status_code == 404

    def test_quest_list_has_mission_counts(self, client, cedar_hollow):
        r = client.get(reverse("v1:quest-list", args=["cedar-hollow"]))
        assert r.status_code == 200
        by_slug = {q["slug"]: q for q in r.json()}
        assert by_slug["savanna-safari"]["mission_count"] == 6
        assert by_slug["savanna-safari"]["badge"]["name"] == "Savanna Scout"
        assert by_slug["savanna-safari"]["is_featured"] is True

    def test_quest_detail_steps_in_order_without_answers(self, client, cedar_hollow):
        r = client.get(reverse("v1:quest-detail", args=["cedar-hollow", "savanna-safari"]))
        assert r.status_code == 200
        steps = r.json()["steps"]
        assert [s["order"] for s in steps] == [1, 2, 3, 4, 5, 6]
        assert steps[-1]["is_final"] is True
        who = next(s["challenge"] for s in steps if s["challenge"]["type"] == "who_am_i")
        assert "options" in who["config"]
        assert "correct" not in who["config"]
        assert who["has_hint"] is False
        assert steps[0]["challenge"]["animal"]["slug"] == "giraffe"

    def test_inactive_quest_is_hidden(self, client, cedar_hollow):
        cedar_hollow.quests.filter(slug="wildlife-detective").update(is_active=False)
        r = client.get(reverse("v1:quest-list", args=["cedar-hollow"]))
        assert {q["slug"] for q in r.json()} == {"savanna-safari", "rainforest-adventure"}

    def test_map_lists_exhibits_with_animals(self, client, cedar_hollow):
        r = client.get(reverse("v1:zoo-map", args=["cedar-hollow"]))
        assert r.status_code == 200
        exhibits = {e["slug"]: e for e in r.json()["exhibits"]}
        assert len(exhibits) == 5
        assert exhibits["african-savanna"]["animal_count"] == 4
        assert {a["slug"] for a in exhibits["reptile-house"]["animals"]} == {"burmese-python", "tortoise"}
        assert float(exhibits["base-camp"]["map_y"]) == 92

    def test_animal_detail(self, client, cedar_hollow):
        r = client.get(reverse("v1:animal-detail", args=["cedar-hollow", "giraffe"]))
        assert r.status_code == 200
        body = r.json()
        assert body["conservation_status_label"] == "Endangered"
        assert len(body["fun_facts"]) == 3
        assert body["exhibit_name"] == "African Savanna"

    def test_marker_lookup_is_case_insensitive(self, client, cedar_hollow):
        r = client.get(reverse("v1:marker-lookup", args=["chz-giraffe-001"]))
        assert r.status_code == 200
        body = r.json()
        assert body["zoo"]["slug"] == "cedar-hollow"
        assert body["animal"] == "giraffe"
        assert body["exhibit_name"] == "African Savanna"

    def test_inactive_marker_is_404(self, client, cedar_hollow):
        cedar_hollow.markers.filter(code="CHZ-GIRAFFE-001").update(is_active=False)
        assert client.get(reverse("v1:marker-lookup", args=["CHZ-GIRAFFE-001"])).status_code == 404
