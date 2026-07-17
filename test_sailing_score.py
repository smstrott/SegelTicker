import unittest

from sailing_score import HourlyConditions, evaluate_window


def conditions(**overrides):
    values = {
        "wind_bft": 4,
        "gust_bft": 5,
        "rain_probability": 0.10,
        "rain_mm": 0,
        "temperature_c": 22,
    }
    values.update(overrides)
    return HourlyConditions(**values)


class EvaluateWindowTest(unittest.TestCase):
    def test_requires_at_least_three_hours(self):
        with self.assertRaises(ValueError):
            evaluate_window([conditions(), conditions()])

    def test_rates_three_ideal_hours_as_excellent(self):
        rating = evaluate_window([conditions(), conditions(), conditions()])

        self.assertEqual(rating.score, 100)
        self.assertEqual(rating.category, "ausgezeichnet")
        self.assertTrue(rating.suitable)

    def test_one_unsafe_hour_invalidates_the_window(self):
        rating = evaluate_window(
            [conditions(), conditions(wind_bft=7, gust_bft=7), conditions()]
        )

        self.assertLessEqual(rating.score, 49)
        self.assertEqual(rating.category, "ungeeignet")
        self.assertFalse(rating.suitable)
        self.assertIn("zeitweise zu viel Wind", rating.reasons)

    def test_strong_gusts_are_reported(self):
        rating = evaluate_window(
            [conditions(), conditions(gust_bft=7), conditions()]
        )

        self.assertFalse(rating.suitable)
        self.assertIn("zu starke Böen", rating.reasons)

    def test_cold_weather_reduces_score_without_becoming_safety_critical(self):
        rating = evaluate_window(
            [conditions(temperature_c=12), conditions(), conditions()]
        )

        self.assertTrue(rating.suitable)
        self.assertIn("kühl", rating.reasons)


if __name__ == "__main__":
    unittest.main()
