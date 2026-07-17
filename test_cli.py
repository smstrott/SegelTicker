import unittest
import tempfile
import json
from unittest.mock import patch

import wind_plot


LOCATIONS = [
    {"name": "Wannsee", "lat": "1", "lon": "2", "channel_id": "3"},
    {"name": "Müggelsee", "lat": "4", "lon": "5", "channel_id": "6"},
]


class CommandLineTest(unittest.TestCase):
    def test_loads_local_sample_json(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json") as sample_file:
            json.dump({"hourly": []}, sample_file)
            sample_file.flush()

            self.assertEqual(
                wind_plot.load_sample_data(sample_file.name),
                {"hourly": []},
            )

    def test_selects_location_case_insensitively(self):
        with patch.object(wind_plot, "config", {"locations": LOCATIONS}):
            selected = wind_plot.select_locations("wannsee")

        self.assertEqual([location["name"] for location in selected], ["Wannsee"])

    def test_rejects_unknown_location_with_available_names(self):
        with patch.object(wind_plot, "config", {"locations": LOCATIONS}):
            with self.assertRaisesRegex(ValueError, "Wannsee, Müggelsee"):
                wind_plot.select_locations("Ostsee")

    def test_dry_run_never_calls_production_release(self):
        with patch.object(
            wind_plot, "config", {"locations": LOCATIONS}
        ), patch.object(
            wind_plot, "preview_location"
        ) as preview, patch.object(
            wind_plot, "release_to_community"
        ) as release:
            wind_plot.run(dry_run=True, location_name="Wannsee")

        preview.assert_called_once_with(LOCATIONS[0], None)
        release.assert_not_called()

    def test_sample_data_automatically_enables_dry_run(self):
        with patch.object(wind_plot, "run") as run:
            wind_plot.main(
                ["--sample-data", "example_wind_data.json", "--location", "Wannsee"]
            )

        run.assert_called_once_with(
            dry_run=True,
            location_name="Wannsee",
            sample_data="example_wind_data.json",
        )


if __name__ == "__main__":
    unittest.main()
