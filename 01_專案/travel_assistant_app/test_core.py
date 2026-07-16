
import pytest
from core import ItineraryGenerator

def test_itinerary_generation():
    gen = ItineraryGenerator()
    destination = "Tokyo, Japan"
    days = 3
    result = gen.generate(destination, days)
    
    assert result["destination"] == destination
    assert "days" in result["duration"]
    assert len(result["itinerary"]) == days

def test_new_destination_added():
    gen = ItineraryGenerator()
    new_dest = "Taipei, Taiwan"
    gen.generate(new_dest, 2)
    assert new_dest in gen.destinations

if __name__ == "__main__":
    pytest.main([__file__])
