from app.services.search_service import SearchService


def test_search_query_parse_defaults() -> None:
    service = SearchService()
    parsed = service.parse_query({"query": "fitness youtubers"})
    assert parsed["platforms"] == ["youtube"]
    assert parsed["region"] is None
    assert parsed["search_queries"]


def test_search_query_parse_follower_and_region_from_nl() -> None:
    service = SearchService()
    parsed = service.parse_query({"query": "find Taiwan english youtuber less than 30000 followers"})
    assert parsed["region"] == "taiwan"
    assert parsed["follower_max"] == 30000
    assert parsed["follower_min"] is None
    assert any("taiwan" in q.lower() for q in parsed["search_queries"])


def test_search_query_parse_between_range() -> None:
    service = SearchService()
    parsed = service.parse_query({"query": "english channels between 10k and 50k subscribers"})
    assert parsed["follower_min"] == 10000
    assert parsed["follower_max"] == 50000
