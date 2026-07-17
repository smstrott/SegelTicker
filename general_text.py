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
    message = (
    "🌤️ *SegelTicker Berlin (v3)*\n"
    "Tägliches Wetter-Update für Segler:innen ⛵️\n\n"
    "🔍 *Analyse der nächsten 2 Tage:*\n"
    "• Gemessene & gefühlte Temperatur\n"
    "• Wind (min/max) & Böen\n"
    "• Regenwahrscheinlichkeit (PoP %)\n"
    "• Regenmenge (mm/h)\n"
    "• Sonnenuntergangszeit\n\n"
    "📊 *Stündliche Visualisierung:*\n"
    "• Zeitraum: 08:00 bis 2h nach Sonnenuntergang\n"
    "• Temperatur, Wind, Regenwahrsch.\n"
    "• Niederschlagsmenge\n\n"
    "✅ *Segeltauglich?* Bewertung nach:\n"
    "• Temperatur > 15 °C\n"
    "• Wind zw. 2–7 Bft\n"
    "• Böen < 6 Bft über Wind\n"
    "• Regenwahrsch. < 60 %\n"
    "• Stündliche Regenmenge. < 0.7 mm/h\n"
    "• Tägliche Regenmenge. < 1.7 mm\n\n"
    "💬 *Fragen, Feedback oder Wünsche?* Schreib an @nafets92"
)
    
    update_msg = (
    "⛵ *SegelTicker Berlin verabschiedet sich in die Winterpause* ☃️\n\n"
    "Die Boote kehren langsam ins Winterlager zurück – und auch der *SegelTicker* legt eine Pause ein.\n"
    "Ab Frühjahr sind wir wieder am Start – mit frischem Wind, neuen Features und aktuellen Segelbedingungen für Berlin!\n\n"
    "Danke an alle, die den Ticker diese Saison genutzt haben.\n"
    "Bleibt dran – wir melden uns rechtzeitig zum Saisonstart zurück!\n\n"
    "📬 Feedback & Ideen? Gerne an @nafets92"
)
    send_telegram_message(
        bot_token,
        chat_id,
        escape_markdown(update_msg),
        disable_notification=False,
    )

if __name__ == "__main__":
    main()
