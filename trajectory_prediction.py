import numpy as np
import pandas as pd


EARTH_RADIUS_M = 6371000.0


def predict_position(lat_deg, lon_deg, speed_mps, heading_deg, dt_sec=60):
    """
    Predict aircraft position after dt_sec seconds using a simple
    constant-velocity motion model.

    Inputs:
    - lat_deg: current latitude in degrees
    - lon_deg: current longitude in degrees
    - speed_mps: ground speed in m/s
    - heading_deg: true track / heading in degrees
    - dt_sec: prediction horizon in seconds

    This is a lightweight motion-model-based prediction, not a
    navigation-grade state estimator.
    """
    if (
        pd.isna(lat_deg)
        or pd.isna(lon_deg)
        or pd.isna(speed_mps)
        or pd.isna(heading_deg)
    ):
        return np.nan, np.nan

    lat = np.radians(lat_deg)
    lon = np.radians(lon_deg)
    heading = np.radians(heading_deg)

    distance = speed_mps * dt_sec

    delta_lat = distance * np.cos(heading) / EARTH_RADIUS_M

    # Avoid division problems near the poles.
    if abs(np.cos(lat)) < 1e-6:
        return np.nan, np.nan

    delta_lon = distance * np.sin(heading) / (EARTH_RADIUS_M * np.cos(lat))

    pred_lat = lat + delta_lat
    pred_lon = lon + delta_lon

    return np.degrees(pred_lat), np.degrees(pred_lon)


def add_position_prediction(df, dt_sec=60):
    """
    Add short-term predicted latitude and longitude to an aircraft state DataFrame.
    Expected columns:
    - latitude
    - longitude
    - velocity
    - true_track
    """
    df = df.copy()

    predictions = df.apply(
        lambda row: predict_position(
            row.get("latitude"),
            row.get("longitude"),
            row.get("velocity"),
            row.get("true_track"),
            dt_sec=dt_sec,
        ),
        axis=1,
    )

    df["pred_latitude"] = [p[0] for p in predictions]
    df["pred_longitude"] = [p[1] for p in predictions]
    df["prediction_horizon_sec"] = dt_sec

    return df
