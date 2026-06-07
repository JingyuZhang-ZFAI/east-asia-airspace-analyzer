import pandas as pd


def classify_flight_phase(row):
    """
    Rule-based flight phase classification using ADS-B state variables.

    Inputs expected in row:
    - altitude_ft: barometric altitude converted to feet
    - vertical_rate: vertical rate in m/s from OpenSky
    - on_ground: whether the aircraft is on ground

    This is a lightweight heuristic classifier, not an operational-grade
    flight phase detection algorithm.
    """
    altitude_ft = row.get("altitude_ft")
    vertical_rate = row.get("vertical_rate")
    on_ground = row.get("on_ground")

    if on_ground is True:
        return "Ground"

    if pd.isna(altitude_ft):
        return "Unknown"

    if pd.isna(vertical_rate):
        vertical_rate = 0

    # OpenSky vertical_rate is in m/s.
    # Positive: climbing; negative: descending.
    if altitude_ft < 10000:
        if vertical_rate > 2:
            return "Takeoff / Initial Climb"
        elif vertical_rate < -2:
            return "Approach / Landing"
        else:
            return "Low Altitude"

    if 10000 <= altitude_ft < 25000:
        if vertical_rate > 2:
            return "Climb"
        elif vertical_rate < -2:
            return "Descent"
        else:
            return "Intermediate Level"

    if altitude_ft >= 25000:
        if abs(vertical_rate) <= 1:
            return "Cruise"
        elif vertical_rate > 1:
            return "High-altitude Climb"
        elif vertical_rate < -1:
            return "High-altitude Descent"

    return "Unknown"


def add_flight_phase(df):
    """
    Add a flight_phase column to an aircraft state DataFrame.
    """
    df = df.copy()
    df["flight_phase"] = df.apply(classify_flight_phase, axis=1)
    return df
