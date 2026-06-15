from comfort_model import comfort_score, mood_from_comfort # Imports the functions that calculate Godzilla's comfort score and mood.
from data_fetcher import CITIES, fetch_weather # Imports the city coordinates and the function that fetches real weather data.


def print_weather_report(city_name): # Receives a city name, gets its weather data, calculates comfort and mood, and prints a readable report.
    city = CITIES[city_name] # Looks up the selected city inside the CITIES dictionary.
    weather = fetch_weather(city["lat"], city["lon"]) # Calls the weather API using the city's latitude and longitude.
    comfort = comfort_score(weather) # Sends the weather dictionary to the comfort model.
    mood = mood_from_comfort(comfort)  # Converts the numeric comfort score into one of Godzilla's moods.

    print(f"\n{city_name}")
    print("-" * len(city_name))
    print(f"Temperature: {weather['temperature']} C")
    print(f"Cloud cover: {weather['cloud_cover']}%")
    print(f"Wind speed:  {weather['wind_speed']} km/h")
    print(f"Rain:        {weather['rain']} mm")
    print(f"Comfort:     {comfort:.2f}")
    print(f"Mood:        {mood}")

# This block only runs when this file is executed directly.
# It does not run if this file is imported into another Python file.
if __name__ == "__main__":
    for city_name in CITIES:
        print_weather_report(city_name)
