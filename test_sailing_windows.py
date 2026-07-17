import unittest
from datetime import datetime, timedelta, timezone

from sailing_score import HourlyConditions
from sailing_windows import (
    ForecastHour,
    evaluate_sailing_windows,
    find_best_sailing_opportunity,
    find_sailing_opportunities,
)


START = datetime(2026, 7, 18, 8, tzinfo=timezone.utc)


def forecast_hour(offset, **overrides):
    values = {
        "wind_bft": 4,
        "gust_bft": 5,
        "rain_probability": 0.10,
        "rain_mm": 0,
        "temperature_c": 22,
    }
    values.update(overrides)
    return ForecastHour(
        START + timedelta(hours=offset),
        HourlyConditions(**values),
    )


class SailingWindowTest(unittest.TestCase):
    def test_evaluates_every_overlapping_three_hour_window(self):
        forecast = [forecast_hour(index) for index in range(5)]

        candidates = evaluate_sailing_windows(forecast)

        self.assertEqual([(item.start_index, item.end_index) for item in candidates], [(0, 3), (1, 4), (2, 5)])

    def test_combines_overlapping_suitable_windows(self):
        forecast = [forecast_hour(index) for index in range(6)]

        opportunities = find_sailing_opportunities(forecast)

        self.assertEqual(len(opportunities), 1)
        self.assertEqual(opportunities[0].duration_hours, 6)
        self.assertEqual(opportunities[0].start, START)
        self.assertEqual(opportunities[0].end, START + timedelta(hours=6))

    def test_unsafe_hour_splits_available_periods(self):
        forecast = [forecast_hour(index) for index in range(9)]
        forecast[4] = forecast_hour(4, wind_bft=8, gust_bft=8)

        opportunities = find_sailing_opportunities(forecast)

        self.assertEqual(len(opportunities), 2)
        self.assertEqual([item.duration_hours for item in opportunities], [4, 4])

    def test_returns_none_when_no_three_hour_window_is_suitable(self):
        forecast = [forecast_hour(index, wind_bft=8, gust_bft=8) for index in range(5)]

        self.assertIsNone(find_best_sailing_opportunity(forecast))

    def test_prefers_longer_window_within_same_score_band(self):
        forecast = [forecast_hour(index) for index in range(10)]
        forecast[3] = forecast_hour(3, wind_bft=8, gust_bft=8)

        best = find_best_sailing_opportunity(forecast)

        self.assertEqual(best.start, START + timedelta(hours=4))
        self.assertEqual(best.duration_hours, 6)


if __name__ == "__main__":
    unittest.main()
