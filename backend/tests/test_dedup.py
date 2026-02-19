from app.services.dedup_service import compute_dedup_status, normalize_profile_url


def test_normalize_profile_url() -> None:
    url = "https://www.youtube.com/@abc/?utm_source=x"
    assert normalize_profile_url(url) == "https://www.youtube.com/@abc"


def test_dedup_by_platform_id(sample_existing_influencers) -> None:
    raw = {
        "platform": "youtube",
        "platform_user_id": "abc123",
        "display_name": "New Name",
        "profile_url": "https://www.youtube.com/@another",
        "follower_count": 1000,
        "email": None,
    }
    status, matched_id = compute_dedup_status(raw, sample_existing_influencers)
    assert status == "duplicate_platform"
    assert matched_id == "11111111-1111-1111-1111-111111111111"


def test_dedup_by_email(sample_existing_influencers) -> None:
    raw = {
        "platform": "youtube",
        "platform_user_id": "new-id",
        "display_name": "Another",
        "profile_url": "https://www.youtube.com/@another",
        "follower_count": 1000,
        "email": "creator1@example.com",
    }
    status, _ = compute_dedup_status(raw, sample_existing_influencers)
    assert status == "duplicate_email"
