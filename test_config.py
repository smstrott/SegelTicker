import json
import tempfile
import unittest

from config_loader import ConfigError, load_config, validate_config


def valid_config():
    return {
        "telegram": {"token": "token", "chat_id": "chat"},
        "openweathermap": {"app_id": "key"},
        "locations": [
            {
                "name": "Wannsee",
                "channel_id": "topic",
                "lat": "52.43",
                "lon": "13.16",
            }
        ],
    }


class ConfigValidationTest(unittest.TestCase):
    def test_accepts_complete_config(self):
        config = valid_config()

        self.assertIs(validate_config(config), config)

    def test_reports_missing_secret(self):
        config = valid_config()
        config["telegram"]["token"] = ""

        with self.assertRaisesRegex(ConfigError, "telegram.token"):
            validate_config(config)

    def test_rejects_duplicate_location_names(self):
        config = valid_config()
        config["locations"].append({**config["locations"][0], "name": "wannsee"})

        with self.assertRaisesRegex(ConfigError, "doppelt"):
            validate_config(config)

    def test_rejects_coordinates_outside_the_globe(self):
        config = valid_config()
        config["locations"][0]["lat"] = "91"

        with self.assertRaisesRegex(ConfigError, "zwischen -90 und 90"):
            validate_config(config)

    def test_reports_invalid_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as config_file:
            config_file.write("{invalid")
            config_file.flush()

            with self.assertRaisesRegex(ConfigError, "ungültiges JSON"):
                load_config(config_file.name)


if __name__ == "__main__":
    unittest.main()
