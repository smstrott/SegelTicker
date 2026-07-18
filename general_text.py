import re
import locale
import os
from telegram_client import send_telegram_message
from config_loader import load_config
try:
    locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
except locale.Error:
    locale.setlocale(locale.LC_TIME, "")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.json")

config = load_config(CONFIG_PATH)

bot_token = config["telegram"]["token"]
chat_id = config["telegram"]["chat_id"]


def escape_markdown(text):
    return re.sub(r'([_\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def main():
    update_msg = (
        "🚀 *SegelTicker Berlin – großes Update* ⛵\n\n"
        "Aus dem Wetterbericht wird ein echter Segelassistent: Ab sofort zeigt der SegelTicker nicht nur die Prognose, sondern wann sich das Segeln wirklich lohnt.\n\n"
        "🕐 *Neue Segelfenster*\n"
        "• Analyse aller Zeiträume ab 3 Stunden\n"
        "• Empfehlung des besten stabilen Segelfensters\n"
        "• Weitere geeignete Zeiträume werden ebenfalls markiert\n"
        "• Verständliche Bewertung von ausgezeichnet bis ungeeignet\n\n"
        "📊 *Komplett neues Dashboard*\n"
        "• Wind und Böen in einer klaren, geglätteten Darstellung\n"
        "• Windrichtung direkt im Winddiagramm\n"
        "• Geeignete Zeiträume auf einen Blick\n"
        "• Sonnenuntergang, Temperatur und Regen übersichtlicher dargestellt\n"
        "• Kompakte Trockenanzeige, wenn kein Regen erwartet wird\n\n"
        "💬 *Kompaktere Nachrichten*\n"
        "• Bestes Zeitfenster, Wind, Böen und Windrichtung\n"
        "• Temperatur, Regenstatus und Sonnenuntergang\n"
        "• Tages-Tendenz für die weiteren Aussichten\n\n"
        "🛡 *Zuverlässiger im Betrieb*\n"
        "Fehler an einem Standort beeinflussen die übrigen Reviere nicht mehr. Wetterabruf und Versand wurden zusätzlich abgesichert.\n\n"
        "Die Bewertung ist zunächst auf typische Freizeitsegler ausgerichtet und wird mit euren Erfahrungen weiter verbessert.\n\n"
        "📬 *Wie gefallen euch die neuen Empfehlungen und Grafiken?*\n"
        "Feedback und Wünsche gerne an @nafets92"
    )
    send_telegram_message(
        bot_token,
        chat_id,
        escape_markdown(update_msg),
        disable_notification=False,
    )

if __name__ == "__main__":
    main()
