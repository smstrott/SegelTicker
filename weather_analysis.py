from datetime import datetime, timezone, timedelta

import pytz

from sailing_score import HourlyConditions
from sailing_windows import (
    ForecastHour,
    find_best_sailing_opportunity,
    find_sailing_opportunities,
)


def wind_speed_to_beaufort(speed):
    thresholds = (0.3, 1.6, 3.4, 5.5, 8.0, 10.8, 13.9, 17.2, 20.8, 24.5, 28.5, 32.7)
    for beaufort, upper_limit in enumerate(thresholds):
        if speed < upper_limit:
            return beaufort
    return 12


def extract_hourly_data(data):
    hourly_wind = [
        (wind_speed_to_beaufort(float(entry.get("wind_speed", 0))), entry.get("dt", 0))
        for entry in data.get("hourly", [])
    ]
    hourly_gust = [
        (wind_speed_to_beaufort(float(entry.get("wind_gust", 0))), entry.get("dt", 0))
        for entry in data.get("hourly", [])
    ]
    hourly_temp = [float(entry.get("temp", 0)) for entry in data.get("hourly", [])]
    hourly_pop = [float(entry.get("pop", 0)) for entry in data.get("hourly", [])]
    hourly_rain = [
        float(entry.get("rain", {}).get("1h", 0))
        for entry in data.get("hourly", [])
    ]
    return hourly_wind, hourly_temp, hourly_pop, hourly_rain, hourly_gust


def convert_timestamp_to_berlin(timestamp):
    utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    return utc_time.astimezone(pytz.timezone("Europe/Berlin"))


def build_sailing_forecast(data):
    return [
        ForecastHour(
            timestamp=convert_timestamp_to_berlin(entry["dt"]),
            conditions=HourlyConditions(
                wind_bft=wind_speed_to_beaufort(float(entry.get("wind_speed", 0))),
                gust_bft=wind_speed_to_beaufort(float(entry.get("wind_gust", 0))),
                rain_probability=float(entry.get("pop", 0)),
                rain_mm=float(entry.get("rain", {}).get("1h", 0)),
                temperature_c=float(entry.get("temp", 0)),
            ),
        )
        for entry in data.get("hourly", [])
    ]


def sailing_forecast_for_day(data, daily_index):
    sunset = convert_timestamp_to_berlin(data["daily"][daily_index]["sunset"])
    window_start = sunset.replace(hour=8, minute=0, second=0, microsecond=0)
    window_end = sunset + timedelta(hours=2)
    return [
        hour
        for hour in build_sailing_forecast(data)
        if window_start <= hour.timestamp < window_end
    ]


def sailing_windows_for_day(data, daily_index):
    return find_sailing_opportunities(sailing_forecast_for_day(data, daily_index))


def best_sailing_window(data, daily_index):
    return find_best_sailing_opportunity(sailing_forecast_for_day(data, daily_index))
