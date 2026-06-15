"""Audit script for the new Godzilla comfort model.

This file is a safe testing sandbox: it copies the new golden_distance formula
locally instead of importing it from comfort_model.py, so the hand-written
annotations in the main model file are not overwritten or affected.

The script fetches about 6 months of real historical weather data for Mexico
City, Tokyo, and Stanford. For each day, it builds a weather dictionary,
calculates a comfort score, converts that score into a Godzilla mood, and then
prints summary statistics for each city.

The goal is to check whether the new formula -- including heat_penalty and
rain ideal = 0.6 -- works well with the proposed mood thresholds:
CURIOUS_THRESHOLD = 0.07 and COZY_THRESHOLD = 0.13.

This script does not change any project files. It only helps us observe the
data, compare comfort percentiles, and decide if the thresholds feel balanced
for the final visual mood system.
"""

import math
from datetime import date, timedelta

from data_fetcher import CITIES, fetch_daily_weather_history


PHI = 1.618
CURIOUS_THRESHOLD = 0.07
COZY_THRESHOLD = 0.13

IDEAL_CLIMATE = {
    "temperature": 18,
    "cloud_cover": 55,
    "wind_speed": 14,
    "rain": 0.6,
}

DAYS_TO_ANALYZE = 180


def golden_distance(weather):
    heat_penalty = max(0, weather["temperature"] - 24)
    return (
        abs(weather["temperature"] - IDEAL_CLIMATE["temperature"]) / 20
        + abs(weather["cloud_cover"] - IDEAL_CLIMATE["cloud_cover"]) / 55
        + abs(weather["wind_speed"] - IDEAL_CLIMATE["wind_speed"]) / 30
        + min(abs(weather["rain"] - IDEAL_CLIMATE["rain"]) / 2.0, 1.0)
        + heat_penalty
    )


def comfort_score(weather):
    return math.exp(-PHI * golden_distance(weather))


def mood_from_comfort(comfort):
    if comfort >= COZY_THRESHOLD:
        return "COZY_ORBIT"
    if comfort >= CURIOUS_THRESHOLD:
        return "CURIOUS_WEATHER"
    return "ANNOYED_GLOW"


def percentile(values, percent):
    ordered_values = sorted(values)
    index = round((len(ordered_values) - 1) * percent)
    return ordered_values[index]


def build_daily_rows(daily_data):
    rows = []
    dates = daily_data["time"]
    temperatures = daily_data["temperature_2m_mean"]
    cloud_covers = daily_data["cloud_cover_mean"]
    wind_speeds = daily_data["wind_speed_10m_mean"]
    rain_values = daily_data["precipitation_sum"]

    for i in range(len(dates)):
        weather = {
            "temperature": temperatures[i],
            "cloud_cover": cloud_covers[i],
            "wind_speed": wind_speeds[i],
            "rain": rain_values[i],
        }
        score = comfort_score(weather)
        rows.append({
            "date": dates[i],
            "weather": weather,
            "comfort": score,
            "mood": mood_from_comfort(score),
        })

    return rows


def print_city_summary(city_name, rows):
    scores = [row["comfort"] for row in rows]
    temperatures = [row["weather"]["temperature"] for row in rows]
    wind_speeds = [row["weather"]["wind_speed"] for row in rows]
    rain_values = [row["weather"]["rain"] for row in rows]
    mood_counts = {"COZY_ORBIT": 0, "CURIOUS_WEATHER": 0, "ANNOYED_GLOW": 0}
    for row in rows:
        mood_counts[row["mood"]] += 1

    n = len(rows)
    print(f"\n{city_name}")
    print("-" * len(city_name))
    print(f"Days analyzed:       {n}")
    print(f"Temperature range:   {min(temperatures):.1f} C to {max(temperatures):.1f} C")
    print(f"Wind speed range:    {min(wind_speeds):.1f} to {max(wind_speeds):.1f} km/h")
    print(f"Rain range:          {min(rain_values):.1f} to {max(rain_values):.1f} mm")
    print(f"Comfort range:       {min(scores):.3f} to {max(scores):.3f}")
    print(
        "Comfort p10/p25/p33/p50/p66/p75/p90: "
        f"{percentile(scores, 0.10):.3f} / {percentile(scores, 0.25):.3f} / "
        f"{percentile(scores, 0.33):.3f} / {percentile(scores, 0.50):.3f} / "
        f"{percentile(scores, 0.66):.3f} / {percentile(scores, 0.75):.3f} / "
        f"{percentile(scores, 0.90):.3f}"
    )
    print(f"Cozy days     (>= {COZY_THRESHOLD}):       {mood_counts['COZY_ORBIT']:3d} ({100*mood_counts['COZY_ORBIT']/n:.0f}%)")
    print(f"Curious days  ({CURIOUS_THRESHOLD}-{COZY_THRESHOLD}):     {mood_counts['CURIOUS_WEATHER']:3d} ({100*mood_counts['CURIOUS_WEATHER']/n:.0f}%)")
    print(f"Annoyed days  (< {CURIOUS_THRESHOLD}):        {mood_counts['ANNOYED_GLOW']:3d} ({100*mood_counts['ANNOYED_GLOW']/n:.0f}%)")


def main():
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=DAYS_TO_ANALYZE)
    all_scores = []

    print(f"Analyzing climate data from {start_date} to {end_date}")
    print(f"Formula: golden_distance with heat_penalty + abs(rain - {IDEAL_CLIMATE['rain']})")
    print(f"Thresholds being tested: CURIOUS={CURIOUS_THRESHOLD}, COZY={COZY_THRESHOLD}")

    for city_name, city in CITIES.items():
        daily_data = fetch_daily_weather_history(city["lat"], city["lon"], start_date, end_date)
        rows = build_daily_rows(daily_data)
        print_city_summary(city_name, rows)
        all_scores.extend(row["comfort"] for row in rows)

    print("\nAll cities combined")
    print("--------------------")
    print(
        "Comfort p10/p25/p33/p50/p66/p75/p90: "
        f"{percentile(all_scores, 0.10):.3f} / {percentile(all_scores, 0.25):.3f} / "
        f"{percentile(all_scores, 0.33):.3f} / {percentile(all_scores, 0.50):.3f} / "
        f"{percentile(all_scores, 0.66):.3f} / {percentile(all_scores, 0.75):.3f} / "
        f"{percentile(all_scores, 0.90):.3f}"
    )


if __name__ == "__main__":
    main()
