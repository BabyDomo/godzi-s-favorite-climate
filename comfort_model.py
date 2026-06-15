import math #calling the math library to use the exp function for calculating comfort score

# Constants for the comfort model
PHI = 1.618 # Golden ratio, used to control the sensitivity of the comfort score to changes in weather conditions. A higher PHI means comfort drops more quickly as conditions deviate from ideal.
CURIOUS_THRESHOLD = 0.0035
COZY_THRESHOLD = 0.15

# Baseline ideal climate conditions for Godzilla's comfort - these values are used to calculate the "golden distance" from the current weather conditions to the ideal ones.
IDEAL_CLIMATE = {
    "temperature": 18,
    "cloud_cover": 55,
    "wind_speed": 14,
    "rain": 0.6,
}

# The "golden distance" is a measure of how far the current weather conditions are from the ideal conditions for Godzilla's comfort. It takes into account the differences in temperature, cloud cover, wind speed, and rain, and applies a heat penalty if the temperature exceeds 21 degrees Celsius.
def golden_distance(weather):
    heat_penalty = max(0, weather["temperature"] - 21) # This variable calculates a penalty for high temperatures, which reduces comfort if the temperature exceeds 21 degrees Celsius.
    # Weather is a dictionary containing the current weather conditions, and we calculate the distance from the ideal climate by taking the absolute difference for each weather parameter, normalizing it, and summing them up. The heat penalty is added to account for discomfort caused by high temperatures.
    return (
        abs(weather["temperature"] - IDEAL_CLIMATE["temperature"]) / 20
        + abs(weather["cloud_cover"] - IDEAL_CLIMATE["cloud_cover"]) / 55
        + abs(weather["wind_speed"] - IDEAL_CLIMATE["wind_speed"]) / 30
        + min(abs(weather["rain"] - IDEAL_CLIMATE["rain"]) / 2.0, 1.0)
        + heat_penalty
    )

# Calculates Godzilla's comfort score from the current weather data.
def comfort_score(weather):
    distance = golden_distance(weather) # Step 1: calculate the "distance" between current weather and ideal weather.
    return math.exp(-PHI * distance) # Step 2: convert that distance into a score between 0 and 1 using exponential decay. If distance is small, comfort stays high. If distance grows, comfort drops quickly.
                                      # PHI controls how sensitive the comfort score is to that distance.

# Returns the correct Godzilla mood depending on how high or low the comfort score is.
def mood_from_comfort(comfort):
    if comfort >= COZY_THRESHOLD:
        return "COZY_ORBIT"
    if comfort >= CURIOUS_THRESHOLD:
        return "CURIOUS_WEATHER"
    return "ANNOYED_GLOW"
