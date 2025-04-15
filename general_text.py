import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone
import pytz
import requests
import json
import requests
import re
from datetime import date, timedelta
import locale
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")


bot_token = "7575140761:AAG6hToLqtRPZb_Xw_NFSaEnFvezZxEUt2w"
test=True
if test == False:
    chat_id = "-1002446565607"  # Beachte das Minus bei Gruppen
else:
    chat_id = "-1002338514550"  # Beachte das Minus bei Gruppen


def send_telegram_message(token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Nachricht gesendet ✅")
    else:
        print("Fehler beim Senden ❌", response.text)

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
    "🔄 *Update SegelTicker Berlin ab dem 12.04.2025* (v2 → v3)\n\n"
    "*Bugfixes:*\n"
    "• Fehler bei der Warnung vor Böen wurde gefixt.\n\n"
    "*Neue Features:*\n"
    "• Regenrisiko und Regenmenge werden nur visualisiert, wenn diese ungleich 0 sind.\n"
    "• Regenmenge wird als Faktor zur Einschätzung des Segeltags berücksichtigt.\n"
    "• Kompaktere Wetter-Zusammenfassung im Ausblick\n"
    "• Einschätzung,ob Gennacker oder Trapez gesegelt werden kann.\n"
    "• Böen werden als hellblaue, gestrichelte Linie mit visualisiert.\n"
    "• Achsenlimits fest statt variabel.\n"
    "💬 *Fragen, Feedback oder Wünsche?* Schreib an @nafets92"
)
    send_telegram_message(bot_token, chat_id, escape_markdown(update_msg))

if __name__ == "__main__":
    main()