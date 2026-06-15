"""Audita el mapeo temperatura -> mood que pide Said:
  18-21 C -> COZY_ORBIT (ideal)
  22-24 C -> CURIOUS_WEATHER (empieza a doler)
  25+  C  -> ANNOYED_GLOW

Compara la formula ACTUAL (heat_penalty arranca en 24, thresholds 0.07/0.13)
contra una formula CANDIDATA (heat_penalty arranca en 21, con pendiente k,
thresholds nuevos), primero con cloud/wind/rain en su valor ideal (para ver
el corte de temperatura "puro"), y despues contra los 6 meses de datos
reales de las 3 ciudades (para ver que la distribucion general siga
teniendo sentido).

No modifica comfort_model.py.
"""

import math
from datetime import date, timedelta

from data_fetcher import CITIES, fetch_daily_weather_history

PHI = 1.618

IDEAL_CLIMATE = {
    "temperature": 18,
    "cloud_cover": 55,
    "wind_speed": 14,
    "rain": 0.6,
}


# ---- formula actual ----
CURRENT_CURIOUS = 0.07
CURRENT_COZY = 0.13


def current_distance(weather):
    heat_penalty = max(0, weather["temperature"] - 24)
    return (
        abs(weather["temperature"] - IDEAL_CLIMATE["temperature"]) / 20
        + abs(weather["cloud_cover"] - IDEAL_CLIMATE["cloud_cover"]) / 55
        + abs(weather["wind_speed"] - IDEAL_CLIMATE["wind_speed"]) / 30
        + min(abs(weather["rain"] - IDEAL_CLIMATE["rain"]) / 2.0, 1.0)
        + heat_penalty
    )


# ---- formula candidata ----
# heat_penalty arranca un grado despues del techo ideal (21) y crece con
# pendiente HEAT_SLOPE -> "duele" cada vez mas rapido a partir de 22.
HEAT_START = 21
HEAT_SLOPE = 0.5
NEW_CURIOUS = 0.04
NEW_COZY = 0.45


def new_distance(weather):
    heat_penalty = max(0, weather["temperature"] - HEAT_START) * HEAT_SLOPE
    return (
        abs(weather["temperature"] - IDEAL_CLIMATE["temperature"]) / 20
        + abs(weather["cloud_cover"] - IDEAL_CLIMATE["cloud_cover"]) / 55
        + abs(weather["wind_speed"] - IDEAL_CLIMATE["wind_speed"]) / 30
        + min(abs(weather["rain"] - IDEAL_CLIMATE["rain"]) / 2.0, 1.0)
        + heat_penalty
    )


def mood(comfort, curious_th, cozy_th):
    if comfort >= cozy_th:
        return "COZY_ORBIT"
    if comfort >= curious_th:
        return "CURIOUS_WEATHER"
    return "ANNOYED_GLOW"


def comfort_score(distance):
    return math.exp(-PHI * distance)


def print_temperature_sweep():
    print("=== Corte de temperatura, resto del clima IDEAL (cloud=55, wind=14, rain=0.6) ===")
    print(f"{'T':>4} | {'actual comfort':>15} {'actual mood':>16} | {'nuevo comfort':>14} {'nuevo mood':>16}")
    for t in range(15, 29):
        weather = {"temperature": t, "cloud_cover": 55, "wind_speed": 14, "rain": 0.6}
        c_old = comfort_score(current_distance(weather))
        c_new = comfort_score(new_distance(weather))
        m_old = mood(c_old, CURRENT_CURIOUS, CURRENT_COZY)
        m_new = mood(c_new, NEW_CURIOUS, NEW_COZY)
        print(f"{t:>4} | {c_old:>15.4f} {m_old:>16} | {c_new:>14.4f} {m_new:>16}")


def build_rows(daily_data, distance_fn):
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
        rows.append((dates[i], weather, comfort_score(distance_fn(weather))))
    return rows


def print_real_data_comparison():
    print("\n=== Distribucion de moods con datos reales (ultimos 180 dias) ===")
    end_date = date.today() - timedelta(days=5)
    start_date = end_date - timedelta(days=180)

    for city_name, city in CITIES.items():
        daily_data = fetch_daily_weather_history(city["lat"], city["lon"], start_date, end_date)
        old_rows = build_rows(daily_data, current_distance)
        new_rows = build_rows(daily_data, new_distance)

        old_counts = {"COZY_ORBIT": 0, "CURIOUS_WEATHER": 0, "ANNOYED_GLOW": 0}
        new_counts = {"COZY_ORBIT": 0, "CURIOUS_WEATHER": 0, "ANNOYED_GLOW": 0}
        for _, _, c in old_rows:
            old_counts[mood(c, CURRENT_CURIOUS, CURRENT_COZY)] += 1
        for _, _, c in new_rows:
            new_counts[mood(c, NEW_CURIOUS, NEW_COZY)] += 1

        n = len(old_rows)
        print(f"\n{city_name} ({n} dias)")
        print(f"  ACTUAL  -> cozy {old_counts['COZY_ORBIT']:3d} ({100*old_counts['COZY_ORBIT']/n:5.1f}%)  "
              f"curious {old_counts['CURIOUS_WEATHER']:3d} ({100*old_counts['CURIOUS_WEATHER']/n:5.1f}%)  "
              f"annoyed {old_counts['ANNOYED_GLOW']:3d} ({100*old_counts['ANNOYED_GLOW']/n:5.1f}%)")
        print(f"  NUEVA   -> cozy {new_counts['COZY_ORBIT']:3d} ({100*new_counts['COZY_ORBIT']/n:5.1f}%)  "
              f"curious {new_counts['CURIOUS_WEATHER']:3d} ({100*new_counts['CURIOUS_WEATHER']/n:5.1f}%)  "
              f"annoyed {new_counts['ANNOYED_GLOW']:3d} ({100*new_counts['ANNOYED_GLOW']/n:5.1f}%)")


if __name__ == "__main__":
    print_temperature_sweep()
    print_real_data_comparison()
