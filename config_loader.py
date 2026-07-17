import json


class ConfigError(ValueError):
    pass


def _required_mapping(config, key):
    value = config.get(key)
    if not isinstance(value, dict):
        raise ConfigError(f"Konfiguration '{key}' fehlt oder ist kein Objekt.")
    return value


def _required_text(config, key, path):
    value = config.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Konfiguration '{path}.{key}' fehlt oder ist leer.")
    return value


def validate_config(config):
    if not isinstance(config, dict):
        raise ConfigError("Die Konfiguration muss ein JSON-Objekt sein.")

    telegram = _required_mapping(config, "telegram")
    _required_text(telegram, "token", "telegram")
    _required_text(telegram, "chat_id", "telegram")

    openweathermap = _required_mapping(config, "openweathermap")
    _required_text(openweathermap, "app_id", "openweathermap")

    locations = config.get("locations")
    if not isinstance(locations, list) or not locations:
        raise ConfigError("Konfiguration 'locations' muss mindestens einen Standort enthalten.")

    names = set()
    for index, location in enumerate(locations):
        path = f"locations[{index}]"
        if not isinstance(location, dict):
            raise ConfigError(f"Konfiguration '{path}' muss ein Objekt sein.")
        name = _required_text(location, "name", path)
        _required_text(location, "channel_id", path)
        latitude = _required_text(location, "lat", path)
        longitude = _required_text(location, "lon", path)

        normalized_name = name.casefold()
        if normalized_name in names:
            raise ConfigError(f"Standortname '{name}' ist doppelt vorhanden.")
        names.add(normalized_name)

        try:
            latitude_value = float(latitude)
            longitude_value = float(longitude)
        except ValueError as error:
            raise ConfigError(
                f"Koordinaten in '{path}' müssen Zahlen sein."
            ) from error
        if not -90 <= latitude_value <= 90:
            raise ConfigError(f"Breitengrad in '{path}' muss zwischen -90 und 90 liegen.")
        if not -180 <= longitude_value <= 180:
            raise ConfigError(f"Längengrad in '{path}' muss zwischen -180 und 180 liegen.")

    return config


def load_config(filename):
    try:
        with open(filename, "r", encoding="utf-8") as config_file:
            config = json.load(config_file)
    except FileNotFoundError as error:
        raise ConfigError(
            f"Konfigurationsdatei nicht gefunden: {filename}. "
            "Kopiere config.example.json nach config.json."
        ) from error
    except json.JSONDecodeError as error:
        raise ConfigError(
            f"Konfigurationsdatei enthält ungültiges JSON: {error}"
        ) from error
    return validate_config(config)
