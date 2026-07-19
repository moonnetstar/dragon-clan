"""旅遊助理 App 的 pytest 測試套件。"""
import pytest

from core import ItineraryGenerator


def test_itinerary_generation():
    """基本行程生成應正常運作。"""
    gen = ItineraryGenerator()
    result = gen.generate("Tokyo, Japan", 3)
    assert result["destination"] == "Tokyo, Japan"
    assert result["duration_days"] == 3
    assert len(result["activities"]) == 3
    assert "generated_at" in result


def test_new_destination_added():
    """非預設目的地應自動加入清單。"""
    gen = ItineraryGenerator()
    assert "Taipei, Taiwan" not in gen.destinations
    gen.generate("Taipei, Taiwan", 2)
    assert "Taipei, Taiwan" in gen.destinations


def test_empty_destination_raises():
    """空目的地應拋出 ValueError。"""
    gen = ItineraryGenerator()
    with pytest.raises(ValueError):
        gen.generate("", 2)


def test_non_positive_days_raises():
    """非正天數應拋出 ValueError。"""
    gen = ItineraryGenerator()
    with pytest.raises(ValueError):
        gen.generate("Tokyo, Japan", 0)
    with pytest.raises(ValueError):
        gen.generate("Tokyo, Japan", -1)


def test_duplicate_destination_not_added_twice():
    """重複目的地不應重複加入。"""
    gen = ItineraryGenerator()
    before = len(gen.destinations)
    gen.generate("Seoul, Korea", 1)
    gen.generate("Seoul, Korea", 1)
    assert len(gen.destinations) == before
