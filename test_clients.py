import unittest
from unittest.mock import Mock, patch

import telegram_client
import weather_client


class WeatherClientTest(unittest.TestCase):
    def test_fetches_metric_german_weather_data(self):
        response = Mock()
        response.json.return_value = {"hourly": []}
        session = Mock()
        session.get.return_value = response

        result = weather_client.fetch_weather_data("api-key", "52.5", "13.2", session)

        self.assertEqual(result, {"hourly": []})
        response.raise_for_status.assert_called_once()
        request = session.get.call_args
        self.assertEqual(request.kwargs["params"]["units"], "metric")
        self.assertEqual(request.kwargs["params"]["lang"], "de")
        self.assertEqual(request.kwargs["timeout"], weather_client.HTTP_TIMEOUT)


class TelegramClientTest(unittest.TestCase):
    def test_sends_message_to_topic_without_retrying_post(self):
        response = Mock()
        with patch.object(telegram_client.requests, "post", return_value=response) as post:
            telegram_client.send_telegram_message(
                "token",
                "chat",
                "message",
                thread_id="topic",
            )

        payload = post.call_args.kwargs["data"]
        self.assertEqual(payload["message_thread_id"], "topic")
        self.assertEqual(payload["parse_mode"], "MarkdownV2")
        self.assertEqual(post.call_args.kwargs["timeout"], telegram_client.HTTP_TIMEOUT)
        response.raise_for_status.assert_called_once()

    def test_omits_topic_when_none_is_given(self):
        response = Mock()
        with patch.object(telegram_client.requests, "post", return_value=response) as post:
            telegram_client.send_telegram_message("token", "chat", "message")

        self.assertNotIn("message_thread_id", post.call_args.kwargs["data"])


if __name__ == "__main__":
    unittest.main()
