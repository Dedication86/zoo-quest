import pytest
from django.urls import reverse

from apps.play.models import Discovery, GuestSession, Scan, XPEvent


def start(client, zoo="cedar-hollow", team=""):
    r = client.post(
        reverse("v1:session-create", args=[zoo]), {"team_name": team}, content_type="application/json"
    )
    assert r.status_code == 201, r.content
    return r.json()


def scan(client, token, code):
    return client.post(
        reverse("v1:scan"), {"code": code}, content_type="application/json", HTTP_X_GUEST_TOKEN=token
    )


@pytest.mark.django_db
class TestSessions:
    def test_start_returns_profile_with_token(self, client, cedar_hollow):
        p = start(client, team="Team Giraffe")
        assert p["team_name"] == "Team Giraffe"
        assert p["total_xp"] == 0
        assert p["level"]["title"] == "Zoo Rookie" and p["level"]["next_at"] == 300
        assert p["stats"]["animals_total"] == 10
        assert GuestSession.objects.get(token=p["token"]).zoo == cedar_hollow

    def test_me_requires_token(self, client, cedar_hollow):
        assert client.get(reverse("v1:me")).status_code == 401

    def test_me_rejects_garbage_token(self, client, cedar_hollow):
        r = client.get(reverse("v1:me"), HTTP_X_GUEST_TOKEN="not-a-uuid")
        assert r.status_code == 401

    def test_patch_team_name(self, client, cedar_hollow):
        token = start(client)["token"]
        r = client.patch(
            reverse("v1:me"),
            {"team_name": "  The Explorers "},
            content_type="application/json",
            HTTP_X_GUEST_TOKEN=token,
        )
        assert r.status_code == 200 and r.json()["team_name"] == "The Explorers"


@pytest.mark.django_db
class TestScan:
    def test_first_scan_discovers_and_awards_xp(self, client, cedar_hollow):
        token = start(client)["token"]
        r = scan(client, token, "chz-giraffe-001")  # lowercase on purpose
        assert r.status_code == 200, r.content
        body = r.json()
        assert body["discovery"] == {"result": "discovery", "is_new": True, "xp": 100}
        assert body["animal"]["slug"] == "giraffe"
        assert len(body["animal"]["fun_facts"]) == 3
        assert body["totals"]["xp"] == 100
        assert body["level_up"] is None
        assert body["suggested_quest"]["slug"] == "savanna-safari"
        assert body["suggested_quest"]["mission_count"] == 6
        assert Discovery.objects.count() == 1
        assert XPEvent.objects.get().amount == 100

    def test_repeat_scan_gives_no_xp_but_is_logged(self, client, cedar_hollow):
        token = start(client)["token"]
        scan(client, token, "CHZ-GIRAFFE-001")
        r = scan(client, token, "CHZ-GIRAFFE-001")
        assert r.status_code == 200
        assert r.json()["discovery"] == {"result": "repeat", "is_new": False, "xp": 0}
        assert r.json()["totals"]["xp"] == 100
        assert Scan.objects.count() == 2
        assert Discovery.objects.count() == 1

    def test_exhibit_marker_without_animal(self, client, cedar_hollow):
        token = start(client)["token"]
        r = scan(client, token, "CHZ-BASECAMP-001")
        assert r.status_code == 200
        assert r.json()["discovery"]["result"] == "exhibit"
        assert r.json()["animal"] is None
        assert r.json()["marker"]["exhibit"]["name"] == "Base Camp"

    def test_level_up_is_reported_once(self, client, cedar_hollow):
        token = start(client)["token"]
        codes = ["CHZ-GIRAFFE-001", "CHZ-ELEPHANT-001", "CHZ-ZEBRA-001"]  # 300 XP = level 2
        results = [scan(client, token, c).json() for c in codes]
        assert results[0]["level_up"] is None and results[1]["level_up"] is None
        assert results[2]["level_up"]["title"] == "Animal Explorer"
        assert results[2]["totals"]["level"]["number"] == 2

    def test_unknown_marker(self, client, cedar_hollow):
        token = start(client)["token"]
        r = scan(client, token, "CHZ-DRAGON-001")
        assert r.status_code == 404 and r.json()["error"] == "unknown_marker"

    def test_inactive_marker(self, client, cedar_hollow):
        cedar_hollow.markers.filter(code="CHZ-LION-001").update(is_active=False)
        token = start(client)["token"]
        r = scan(client, token, "CHZ-LION-001")
        assert r.status_code == 410 and r.json()["error"] == "inactive_marker"

    def test_marker_from_another_zoo_is_refused(self, client, cedar_hollow):
        from apps.tenants.models import Zoo

        other = Zoo.objects.create(name="Other Zoo", slug="other")
        token = start(client, zoo="other")["token"]
        r = scan(client, token, "CHZ-GIRAFFE-001")
        assert r.status_code == 400 and r.json()["error"] == "wrong_zoo"
        assert other.guestsessions.count() == 1

    def test_scan_requires_token(self, client, cedar_hollow):
        assert scan(client, "", "CHZ-GIRAFFE-001").status_code in (401, 403)

    def test_profile_reflects_discoveries(self, client, cedar_hollow):
        token = start(client)["token"]
        scan(client, token, "CHZ-SLOTH-001")
        scan(client, token, "CHZ-TORTOISE-001")
        p = client.get(reverse("v1:me"), HTTP_X_GUEST_TOKEN=token).json()
        assert p["total_xp"] == 200
        assert p["stats"]["animals_discovered"] == 2 and p["stats"]["scans"] == 2
        assert [d["slug"] for d in p["discoveries"]] == ["sloth", "tortoise"]
