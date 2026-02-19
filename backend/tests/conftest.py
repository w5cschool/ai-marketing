import os

import pytest

os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"


@pytest.fixture
def sample_existing_influencers() -> list[dict]:
    return [
        {
            "id": "11111111-1111-1111-1111-111111111111",
            "platform": "youtube",
            "platform_user_id": "abc123",
            "display_name": "Creator One",
            "profile_url": "https://www.youtube.com/@creatorone",
            "follower_count": 50000,
            "email": "creator1@example.com",
        }
    ]
