"""Response schemas read the right attributes from database models."""
from datetime import datetime

from app.api.v1.schemas import BadgeResponse
from app.db.models import BadgeType, UserBadge


def test_badge_details_come_from_the_badge_row():
    # On a model, `metadata` is SQLAlchemy's table registry, so the badge
    # column is called `details`; a schema field named `metadata` would read
    # the registry instead of the row.
    badge = UserBadge(
        id=1,
        user_id=1,
        badge_type=BadgeType.FIRST_SESSION,
        earned_at=datetime(2026, 1, 1),
        details={"sessions": 1},
    )

    assert BadgeResponse.model_validate(badge).details == {"sessions": 1}
