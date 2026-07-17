import logging

import requests


HTTP_TIMEOUT = (5, 20)
logger = logging.getLogger(__name__)


def send_telegram_message(
    token,
    chat_id,
    message,
    thread_id=None,
    disable_notification=True,
):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "disable_notification": disable_notification,
    }
    if thread_id is not None:
        payload["message_thread_id"] = thread_id

    response = requests.post(url, data=payload, timeout=HTTP_TIMEOUT)
    response.raise_for_status()
    logger.info("Telegram-Nachricht gesendet")


def send_telegram_photo(
    token,
    chat_id,
    thread_id,
    filename,
    tag,
    disable_notification=True,
):
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    with open(filename, "rb") as photo:
        response = requests.post(
            url,
            files={"photo": photo},
            data={
                "chat_id": chat_id,
                "message_thread_id": thread_id,
                "caption": f"📊 Wetter {tag}",
                "disable_notification": disable_notification,
            },
            timeout=HTTP_TIMEOUT,
        )
    response.raise_for_status()
    logger.info("Telegram-Foto gesendet: %s", filename)
