from datetime import date, timedelta # Imports date tools to define the historical analysis window.

from comfort_model import comfort_score, mood_from_comfort  # Imports the model that converts weather into comfort and mood.
from data_fetcher import CITIES, fetch_daily_weather_history # Imports city coordinates and historical weather fetcher.


DAYS_TO_ANALYZE = 180 # Number of past days used to calibrate the comfort thresholds.


def percentile(values, percent): # Returns the approximate value at a given percentile inside a sorted list.
    ordered_values = sorted(values)
    index = round((len(ordered_values) - 1) * percent)
    return ordered_values[index]


def build_daily_weather_rows(daily_data): # Converts raw daily API arrays into one clean row per day with weather, comfort, and mood.
    rows = []
    dates = daily_data["time"]
    temperatures = daily_data["temperature_2m_mean"]
    cloud_covers = daily_data["cloud_cover_mean"]
    wind_speeds = daily_data["wind_speed_10m_mean"]
    rain_values = daily_data["precipitation_sum"]

    for i in range(len(dates)): # Loops through every day and builds a weather dictionary for that specific date.
        weather = {
            "temperature": temperatures[i],
            "cloud_cover": cloud_covers[i],
            "wind_speed": wind_speeds[i],
            "rain": rain_values[i],
        }
        score = comfort_score(weather)
        rows.append(
            {
                "date": dates[i],
                "weather": weather,
                "comfort": score,
                "mood": mood_from_comfort(score),
            }
        )

    return rows


def print_city_summary(city_name, rows):
    scores = [row["comfort"] for row in rows]
    temperatures = [row["weather"]["temperature"] for row in rows]
    cloud_covers = [row["weather"]["cloud_cover"] for row in rows]
    wind_speeds = [row["weather"]["wind_speed"] for row in rows]
    rain_values = [row["weather"]["rain"] for row in rows]
    mood_counts = {
        "COZY_ORBIT": 0,
        "CURIOUS_WEATHER": 0,
        "ANNOYED_GLOW": 0,
    }

    for row in rows:
        mood_counts[row["mood"]] += 1

    print(f"\n{city_name}")
    print("-" * len(city_name))
    print(f"Days analyzed: {len(rows)}")
    print(f"Temperature range: {min(temperatures):.1f} C to {max(temperatures):.1f} C")
    print(f"Cloud cover range: {min(cloud_covers):.0f}% to {max(cloud_covers):.0f}%")
    print(f"Wind speed range:  {min(wind_speeds):.1f} km/h to {max(wind_speeds):.1f} km/h")
    print(f"Rain range:        {min(rain_values):.1f} mm to {max(rain_values):.1f} mm")
    print(f"Comfort range:     {min(scores):.2f} to {max(scores):.2f}")
    print(f"Comfort p33/p66:   {percentile(scores, 0.33):.2f} / {percentile(scores, 0.66):.2f}")
    print(f"Cozy days:         {mood_counts['COZY_ORBIT']}")
    print(f"Curious days:      {mood_counts['CURIOUS_WEATHER']}")
    print(f"Annoyed days:      {mood_counts['ANNOYED_GLOW']}")


def main():
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=DAYS_TO_ANALYZE)
    all_scores = []

    print(f"Analyzing climate data from {start_date} to {end_date}")

    for city_name, city in CITIES.items():
        daily_data = fetch_daily_weather_history(city["lat"], city["lon"], start_date, end_date)
        rows = build_daily_weather_rows(daily_data)
        print_city_summary(city_name, rows)
        all_scores.extend(row["comfort"] for row in rows)

    print("\nRecommended mood thresholds from all cities")
    print("-------------------------------------------")
    print(f"CURIOUS_WEATHER starts near: {percentile(all_scores, 0.33):.2f}")
    print(f"COZY_ORBIT starts near:      {percentile(all_scores, 0.66):.2f}")


if __name__ == "__main__":
    main()
