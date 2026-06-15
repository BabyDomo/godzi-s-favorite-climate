import requests # Imports the requests library, which lets Python talk to websites and APIs through the internet.

# URL used to get current weather data from Open-Meteo.
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# URL used to get historical weather data from Open-Meteo.
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"


# Dictionary of preset cities.
# Each city name points to another dictionary with its latitude and longitude.
# These coordinates are needed because the weather API does not search by city name here;
# it needs exact geographic coordinates.
CITIES = {
    "Mexico City": {"lat": 19.4326, "lon": -99.1332},
    "Stanford": {"lat": 37.4419, "lon": -122.1430},
    "Tokyo": {"lat": 35.6762, "lon": 139.6503},
}

# Default weather data used if the API request fails.
# This keeps the program from crashing if there is no internet, the API is down,
# or the response does not contain the expected data.
FALLBACK_WEATHER = {
    "temperature": 20.0,
    "cloud_cover": 50,
    "wind_speed": 10.0,
    "rain": 0.0,
}


def fetch_weather(lat, lon): # Gets current weather data for one location using latitude and longitude.
    params = { # Parameters sent to the Open-Meteo API.
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,cloud_cover,wind_speed_10m,rain",
    }
    # Sends a GET request to the Open-Meteo API.
    # params=params adds the weather parameters to the URL automatically.
    # timeout=10 means Python will stop waiting after 10 seconds if the API does not respond.
    try:
        response = requests.get(OPEN_METEO_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json() # Converts the API response from JSON text into a Python dictionary.
        current = data["current"]

    # Returns a new dictionary with clean names for our project.
    # The API uses names like "temperature_2m" and "wind_speed_10m",
    # but our Godzilla project uses simpler names like "temperature" and "wind_speed"

        return {
            "temperature": current["temperature_2m"],
            "cloud_cover": current["cloud_cover"],
            "wind_speed": current["wind_speed_10m"],
            "rain": current["rain"],
        }
    except (requests.RequestException, KeyError): # Returns a safe fallback weather if there is an error with the API request or the response data is not in the expected format.
        return FALLBACK_WEATHER.copy()


def fetch_daily_weather_history(lat, lon, start_date, end_date): # Gets historical daily weather data for one location and date range.
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "daily": "temperature_2m_mean,cloud_cover_mean,wind_speed_10m_mean,precipitation_sum",
        "timezone": "auto",
    }

    response = requests.get(ARCHIVE_URL, params=params, timeout=20)
    response.raise_for_status()
    return response.json()["daily"]
