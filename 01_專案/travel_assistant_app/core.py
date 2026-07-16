
import datetime
import random

class ItineraryGenerator:
    def __init__(self):
        self.destinations = ["Tokyo, Japan", "Paris, France", "New York, USA", "London, UK", "Seoul, South Korea"]

    def generate(self, destination, duration_days):
        if destination not in self.destinations:
            # Simulate adding new destination
            self.destinations.append(destination)
        
        itinerary = []
        activities = ["Visit Museum", "Eat Local Food", "Walk in Park", "Shopping Trip", "Photography Session"]
        
        for day in range(1, duration_days + 1):
            day_plan = {
                "day": day,
                "activities": random.sample(activities, min(len(activities), 2))
            }
            itinerary.append(day_plan)
            
        return {
            "destination": destination,
            "duration": f"{duration_days} days",
            "itinerary": itinerary,
            "generated_at": datetime.datetime.now().isoformat()
        }

if __name__ == "__main__":
    gen = ItineraryGenerator()
    result = gen.generate("Tokyo, Japan", 3)
    print(f"Generated Itinerary for {result['destination']}:")
    for day in result['itienteary'] if 'itienteary' in result else result['itinerary']:
        print(f" Day {day['day']}: {', '.join(day['activities'])}")
