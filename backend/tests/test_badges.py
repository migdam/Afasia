"""Every badge type can be earned (backlog P2-9d). The three that had no
rule for earning them (perfectionist, dedicated, master) were removed;
which achievements to add, if any, is a product decision (H7)."""
import re
from pathlib import Path

from app.db.models import BadgeType
from test_recordings import register
from test_rest_days import on_day, practise  # noqa: F401 - on_day is a fixture

UI = Path(__file__).resolve().parents[2] / "frontend" / "js" / "ui.js"


def badges(client, auth):
    return sorted(b["badge_type"] for b in client.get("/api/v1/users/badges", headers=auth).json())


def test_only_badges_that_can_be_earned_exist():
    assert {b.value for b in BadgeType} == {"first_session", "week_streak", "month_streak"}


def test_the_app_has_an_icon_for_every_badge_and_no_others():
    icons = re.search(r"const badgeIcons = \{(.*?)\};", UI.read_text(), re.S).group(1)

    assert set(re.findall(r"(\w+):", icons)) == {b.value for b in BadgeType}


def test_seven_practice_days_with_days_off_between_earn_the_week_badge(client, on_day):
    pat = register(client, "pat")

    practise(client, pat, on_day, *range(0, 14, 2))

    assert badges(client, pat) == ["first_session", "week_streak"]


def test_thirty_practice_days_earn_the_month_badge(client, on_day):
    pat = register(client, "pat")

    practise(client, pat, on_day, *range(30))

    assert badges(client, pat) == ["first_session", "month_streak", "week_streak"]
