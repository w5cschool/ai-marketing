from urllib.parse import urlparse


def normalize_profile_url(url: str) -> str:
    parsed = urlparse(url.strip())
    path = parsed.path.rstrip("/")
    netloc = parsed.netloc.lower()
    scheme = parsed.scheme.lower() or "https"
    return f"{scheme}://{netloc}{path}"


def follower_bucket(follower_count: int | None) -> str:
    if follower_count is None:
        return "unknown"
    if follower_count < 10000:
        return "0-10k"
    if follower_count < 100000:
        return "10k-100k"
    if follower_count < 1000000:
        return "100k-1m"
    return "1m+"


def compute_dedup_status(raw: dict, existing: list[dict]) -> tuple[str, str | None]:
    platform_user_id = raw.get("platform_user_id")
    platform = raw.get("platform")
    normalized_url = normalize_profile_url(raw.get("profile_url", ""))
    email = (raw.get("email") or "").strip().lower()

    for item in existing:
        if item.get("platform") == platform and item.get("platform_user_id") == platform_user_id:
            return "duplicate_platform", item.get("id")

    for item in existing:
        if normalize_profile_url(item.get("profile_url", "")) == normalized_url and normalized_url:
            return "duplicate_url", item.get("id")

    if email:
        for item in existing:
            if ((item.get("email") or "").strip().lower()) == email:
                return "duplicate_email", item.get("id")

    weak = [
        item
        for item in existing
        if item.get("platform") == platform
        and item.get("display_name", "").strip().lower() == (raw.get("display_name", "").strip().lower())
        and follower_bucket(item.get("follower_count")) == follower_bucket(raw.get("follower_count"))
    ]
    if weak:
        return "weak_match", weak[0].get("id")

    return "unique", None
