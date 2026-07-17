import unittest
from datetime import datetime, timedelta, timezone

from wind_plot import (
    best_sailing_window,
    compass_direction,
    format_day_message,
    format_daily_outlook,
    format_sailing_assessment,
    format_sailing_reasons,
    format_sailing_window,
    smooth_hourly_series,
)


START = datetime(2026, 7, 18, 6, tzinfo=timezone.utc)


def weather_data(wind_speed=6.0, wind_gust=8.0):
    return {
        "daily": [
            {
                "dt": int((START + timedelta(hours=6)).timestamp()),
                "sunset": int((START + timedelta(hours=14)).timestamp()),
            }
        ],
        "hourly": [
            {
                "dt": int((START + timedelta(hours=index)).timestamp()),
                "wind_speed": wind_speed,
                "wind_gust": wind_gust,
                "pop": 0.1,
                "rain": {"1h": 0},
                "temp": 22,
            }
            for index in range(6)
        ],
    }


class SailingIntegrationTest(unittest.TestCase):
    def test_formats_daily_outlook_as_tendency(self):
        day = {
            "wind_speed": 6.0,
            "wind_gust": 8.0,
            "temp": {"day": 21},
            "pop": 0.1,
        }

        outlook = format_daily_outlook(day)

        self.assertIn("gute Tendenz", outlook)
        self.assertIn("4 Bft, Böen 5", outlook)

    def test_daily_outlook_reports_rain(self):
        day = {
            "wind_speed": 6.0,
            "wind_gust": 8.0,
            "temp": {"day": 21},
            "pop": 0.8,
            "rain": 3.2,
        }

        outlook = format_daily_outlook(day)

        self.assertIn("regnerisch", outlook)
        self.assertIn("Regen 80 %", outlook)

    def test_formats_compass_directions(self):
        self.assertEqual(compass_direction(0), "Nord")
        self.assertEqual(compass_direction(90), "Ost")
        self.assertEqual(compass_direction(225), "Südwest")

    def test_formats_compact_daily_message(self):
        message = format_day_message(weather_data(), 0, "Heute")

        self.assertIn("Heute: ausgezeichnete Segelbedingungen", message)
        self.assertIn("08:00–14:00 Uhr", message)
        self.assertIn("Wind: 4–4 Bft", message)
        self.assertIn("Richtung: Nord", message)
        self.assertIn("Regenrisiko bis 10 %", message)

    def test_smooth_curve_keeps_real_values_and_does_not_overshoot(self):
        timestamps = [START, START + timedelta(hours=1), START + timedelta(hours=2)]
        smooth_times, smooth_values = smooth_hourly_series(timestamps, [2, 5, 1])

        self.assertEqual(smooth_times[0], timestamps[0])
        self.assertEqual(smooth_times[-1], timestamps[-1])
        self.assertEqual(smooth_values[0], 2)
        self.assertEqual(smooth_values[-1], 1)
        self.assertGreaterEqual(min(smooth_values), 1)
        self.assertLessEqual(max(smooth_values), 5)

    def test_finds_window_in_openweather_data(self):
        opportunity = best_sailing_window(weather_data(), 0)

        self.assertIsNotNone(opportunity)
        self.assertEqual(opportunity.duration_hours, 6)
        self.assertEqual(opportunity.start.strftime("%H:%M"), "08:00")
        self.assertEqual(opportunity.end.strftime("%H:%M"), "14:00")
        self.assertEqual(
            format_sailing_assessment(opportunity),
            "ausgezeichnete Segelbedingungen",
        )
        self.assertIn("stabil", format_sailing_reasons(opportunity))

    def test_returns_no_window_for_unsafe_openweather_data(self):
        opportunity = best_sailing_window(
            weather_data(wind_speed=18.0, wind_gust=20.0),
            0,
        )

        self.assertIsNone(opportunity)
        self.assertIn("Kein stabiles Segelfenster", format_sailing_window(opportunity))
        self.assertEqual(
            format_sailing_assessment(opportunity),
            "kein geeignetes Segelfenster",
        )


if __name__ == "__main__":
    unittest.main()
