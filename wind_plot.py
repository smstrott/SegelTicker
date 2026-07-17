import argparse
import json
import locale
import logging
import os

from dashboard_plot import (
    plot_dashboard,
    plot_wind_speed,
    smooth_hourly_series,
    temperature_axis_max,
)
from config_loader import load_config
from message_formatter import (
    compass_direction,
    create_message,
    escape_markdown,
    format_daily_outlook,
    format_day_message,
    format_sailing_assessment,
    format_sailing_reasons,
    format_sailing_window,
)
from telegram_client import send_telegram_message, send_telegram_photo
from weather_analysis import (
    best_sailing_window,
    build_sailing_forecast,
    convert_timestamp_to_berlin,
    extract_hourly_data,
    sailing_forecast_for_day,
    sailing_windows_for_day,
    wind_speed_to_beaufort,
)
from weather_client import fetch_weather_data as request_weather_data


try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

config = load_config(CONFIG_PATH)

bot_token = config["telegram"]["token"]
chat_id = config["telegram"]["chat_id"]
app_id = config["openweathermap"]["app_id"]


def fetch_weather_data(lat, lon):
    return request_weather_data(app_id, lat, lon)


def create_location_output(data, location):
    hourly_wind, hourly_temp, pop, hourly_rain, hourly_gust = extract_hourly_data(data)
    message = create_message(data, location)
    plot_wind_speed(
        data,
        hourly_wind,
        hourly_gust,
        hourly_temp,
        pop,
        hourly_rain,
        location,
    )
    return message


def release_to_community(lat, lon, thread_id, location):
    data = fetch_weather_data(lat, lon)
    message = create_location_output(data, location)
    send_telegram_message(bot_token, chat_id, message, thread_id)
    send_telegram_photo(
        bot_token,
        chat_id,
        thread_id,
        f"{location}_wetter_heute.png",
        "heute",
    )
    send_telegram_photo(
        bot_token,
        chat_id,
        thread_id,
        f"{location}_wetter_morgen.png",
        "morgen",
    )


def select_locations(location_name=None):
    if location_name is None:
        return config["locations"]

    selected = [
        location
        for location in config["locations"]
        if location["name"].casefold() == location_name.casefold()
    ]
    if not selected:
        available = ", ".join(location["name"] for location in config["locations"])
        raise ValueError(
            f"Unbekannter Standort '{location_name}'. Verfügbar: {available}"
        )
    return selected


def load_sample_data(filename):
    with open(filename, "r", encoding="utf-8") as sample_file:
        return json.load(sample_file)


def preview_location(location, data=None):
    if data is None:
        data = fetch_weather_data(location["lat"], location["lon"])
    message = create_location_output(data, location["name"])
    print(f"\n--- Vorschau: {location['name']} ---\n")
    print(message)
    print(
        f"\nBilder: {location['name']}_wetter_heute.png, "
        f"{location['name']}_wetter_morgen.png"
    )


def run(dry_run=False, location_name=None, sample_data=None):
    locations = select_locations(location_name)
    sample = load_sample_data(sample_data) if sample_data else None
    failed_locations = []
    for location in locations:
        try:
            if dry_run or sample is not None:
                preview_location(location, sample)
            else:
                release_to_community(
                    location["lat"],
                    location["lon"],
                    location["channel_id"],
                    location["name"],
                )
        except Exception:
            failed_locations.append(location["name"])
            logger.exception(
                "Standort %s konnte nicht verarbeitet werden; fahre fort",
                location["name"],
            )

    if failed_locations:
        raise RuntimeError(
            "Fehlgeschlagene Standorte: " + ", ".join(failed_locations)
        )


def parse_args(arguments=None):
    parser = argparse.ArgumentParser(
        description="SegelTicker erzeugen und optional an Telegram senden."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nachricht und Bilder lokal erzeugen, niemals an Telegram senden.",
    )
    parser.add_argument(
        "--location",
        help="Nur einen konfigurierten Standort verarbeiten, z. B. Wannsee.",
    )
    parser.add_argument(
        "--sample-data",
        metavar="JSON",
        help="Lokale OpenWeather-JSON verwenden; aktiviert automatisch Dry-Run.",
    )
    return parser.parse_args(arguments)


def main(arguments=None):
    args = parse_args(arguments)
    run(
        dry_run=args.dry_run or args.sample_data is not None,
        location_name=args.location,
        sample_data=args.sample_data,
    )


if __name__ == "__main__":
    main()
