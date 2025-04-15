import json
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone
import pytz
import requests
import json
import requests
import re
import locale
locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")

with open("config.json", "r") as f:
    config = json.load(f)

bot_token = config["telegram"]["token"]
chat_id = config["telegram"]["chat_id"]
app_id = config["openweathermap"]["app_id"]

def send_telegram_message(token, chat_id, message, thread_id):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "MarkdownV2",
        "message_thread_id": thread_id
    }
    response = requests.post(url, data=payload)
    if response.status_code == 200:
        print("Nachricht gesendet ✅")
    else:
        print("Fehler beim Senden ❌", response.text)

def send_telegram_photo(thread_id, Dateiname, Tag):
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    with open(Dateiname, "rb") as foto:
        files = {"photo": foto}
        data = {"chat_id": chat_id, "message_thread_id": thread_id, "caption": f"📊 Wetter {Tag}"}
        response = requests.post(url, files=files, data=data)
    if response.status_code == 200:
        print("Nachricht gesendet ✅")
    else:
        print("Fehler beim Senden ❌", response.text)

def import_json(lat, lon):
    # URL der JSON-Datei
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&appid={app_id}&units=metric&lang=de"

    # JSON-Daten abrufen
    response = requests.get(url)

    # Prüfen, ob der Download erfolgreich war
    if response.status_code == 200:
        data = response.json()  # Als Python-Datenstruktur laden

        # In Datei speichern
        with open("wind_data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        print("Datei erfolgreich gespeichert.")
    else:
        print("Fehler beim Herunterladen:", response.status_code)
    return load_json("wind_data.json")

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def wind_speed_to_beaufort(speed):
    if speed < 0.3:
        return 0
    elif speed < 1.6:
        return 1
    elif speed < 3.4:
        return 2
    elif speed < 5.5:
        return 3
    elif speed < 8.0:
        return 4
    elif speed < 10.8:
        return 5
    elif speed < 13.9:
        return 6
    elif speed < 17.2:
        return 7
    elif speed < 20.8:
        return 8
    elif speed < 24.5:
        return 9
    elif speed < 28.5:
        return 10
    elif speed < 32.7:
        return 11
    else:
        return 12

def extract_daily_data(data):
    temps_day = [day["temp"]["day"] for day in data["daily"]]
    feels_like_day = [day["feels_like"]["day"] for day in data["daily"]]
    winds_day = [day["wind_speed"] for day in data["daily"]]
    dt_day = [day["dt"] for day in data["daily"]]
    winds_gust_day = [day["wind_gust"] for day in data["daily"]]
    pops_day = [day["pop"] for day in data["daily"]]
    description_day = [day["weather"][0]["description"] for day in data["daily"]]
    print
    daily_rain = []
    for regen in data["daily"]:
        if "rain" in regen:
            daily_rain.append(regen["rain"])
        else:
            daily_rain.append(0)

    return temps_day, feels_like_day, winds_day, winds_gust_day, pops_day, dt_day, daily_rain, description_day

def extract_hourly_data(data):
    hourly_wind = [(wind_speed_to_beaufort(float(entry.get("wind_speed", 0))), entry.get("dt", 0)) for entry in data.get("hourly", [])]
    hourly_gust = [(wind_speed_to_beaufort(float(entry.get("wind_gust", 0))), entry.get("dt", 0)) for entry in data.get("hourly", [])]
    hourly_temp = [(float(entry.get("temp", 0))) for entry in data.get("hourly", [])]
    hourly_pop = [(float(entry.get("pop", 0))) for entry in data.get("hourly", [])]
    hourly_rain = []

    for hour in data["hourly"]:
        if "rain" in hour and "1h" in hour["rain"]:
            hourly_rain.append(hour["rain"]["1h"])
        else:
            hourly_rain.append(0)

    return hourly_wind, hourly_temp, hourly_pop, hourly_rain, hourly_gust

def convert_timestamp_to_berlin(timestamp):
    utc_time = datetime.fromtimestamp(timestamp, tz=timezone.utc)
    berlin_tz = pytz.timezone("Europe/Berlin")
    berlin_time = utc_time.astimezone(berlin_tz)
    return berlin_time

def plot (day, Location, hourly_indices, hourly_labels, hourly_speeds, hourly_gust_speeds, today_end, tomorrow_start, tomorrow_end, date_titel,hourly_temp, hourly_rain, pop):
    if day == "today":
        titel = 0
        range_start = 0
        range_end = today_end
        file_end = "heute"
    if day == "tomorrow":
        titel = 24
        range_start = tomorrow_start
        range_end = tomorrow_end
        file_end = "morgen"

    # Plot Settings 
    bar_width = 0.4 #Breite der Regenbalken
    x = np.arange(len(hourly_indices[range_start:range_end]))+titel  # Alternativ zu den Labels, für numerische Positionen
    color_boeen="dodgerblue"
    color_wind="navy"
    color_temp="tab:red"
    color_pop="mediumseagreen"
    color_regenmenge="skyblue"
    fig, ax1 = plt.subplots(figsize=(10, 5))
    fig.suptitle(f"{Location} {date_titel[titel]}: Wind, Temperatur & Niederschlag", fontsize=14, y=0.90)
    ax1.set_xlabel('Zeit')
    ax1.set_ylabel('Beaufort Scale', color=color_wind)
    ax1.plot(hourly_indices[range_start:range_end], hourly_gust_speeds[range_start:range_end], color=color_boeen, label='Böen', linestyle='--')
    ax1.plot(hourly_indices[range_start:range_end], hourly_speeds[range_start:range_end], color=color_wind, label='Wind', linestyle='-')
    ax1.tick_params(axis='y', labelcolor=color_wind)
    ax1.set_xticks(hourly_indices[range_start:range_end])
    ax1.set_xticklabels(hourly_labels[range_start:range_end], rotation=45, ha='right')
    ax1.grid(True, linestyle='--', linewidth=0.5, alpha=0.7)
    if any(max > 10 for max in hourly_gust_speeds[range_start:range_end]):
        ax1.set_ylim(0, 15)
    else:
        ax1.set_ylim(0, 8)

    ax2 = ax1.twinx()
    ax2.set_ylabel("Temperatur (°C)", color=color_temp)
    ax2.plot(hourly_indices[range_start:range_end], hourly_temp[range_start:range_end], color=color_temp, label="Temperatur", linestyle='-')
    ax2.tick_params(axis='y', labelcolor=color_temp)
    ax2.set_ylim(0, 35)
    if any(po != 0 for po in pop[range_start:range_end]):
        ax3 = ax1.twinx()
        ax3.spines["right"].set_position(("axes", 1.09))
        ax3.set_frame_on(True)
        ax3.patch.set_visible(False)
        ax3.set_ylabel("Regenwahrsch. (%)", color=color_pop)
        ax3.bar(x - bar_width / 4, [p * 100 for p in pop[range_start:range_end]], width=bar_width, color=color_pop, alpha=0.3, label="Regenrisiko")
        ax3.tick_params(axis='y', labelcolor=color_pop)
        ax3.set_ylim(0, 100)

    if any(hr != 0 for hr in hourly_rain[range_start:range_end]):
        ax4 = ax1.twinx()
        ax4.spines["right"].set_position(("axes", 1.18))
        ax4.set_frame_on(True)
        ax4.patch.set_visible(False)
        ax4.set_ylabel("Regenmenge (mm/h)", color=color_regenmenge)
        ax4.bar(x + bar_width / 4, hourly_rain[range_start:range_end], width=bar_width, color=color_regenmenge, alpha=0.3, label="Regenmenge")
        ax4.tick_params(axis='y', labelcolor=color_regenmenge)
        if any(max_r > 3 for max_r in hourly_rain[range_start:range_end]):
            ax4.set_ylim(0, 10)
        else:
            ax4.set_ylim(0, 3)

    fig.legend(loc='lower center', bbox_to_anchor=(0.5, -0.005), ncol=5, frameon=True)
    fig.tight_layout(rect=[0, 0.05, 1, 0.95])
    plt.savefig(f"{Location}_wetter_{file_end}.png", dpi=300, bbox_inches='tight')
    plt.close() 

def plot_wind_speed(hourly_wind, hourly_gust, hourly_temp, pop, hourly_rain, hour_sunset, Location):

    hourly_speeds, hourly_timestamps = zip(*hourly_wind)
    hourly_gust_speeds, hourly_gust_timestamps = zip(*hourly_gust)
    hourly_labels = [convert_timestamp_to_berlin(ts).strftime('%H:%M') for ts in hourly_timestamps]
    hourly_indices = np.linspace(0, len(hourly_labels)-1, len(hourly_labels))
    today_end=int(hour_sunset)-6
    tomorrow_start=24
    tomorrow_end=int(hour_sunset)-6+24
    date_titel = [convert_timestamp_to_berlin(ts).strftime('%a, %d.%m.') for ts in hourly_timestamps]

    # ------------------------
    # Hourly Wind/Temp/PoP Plot
    # ------------------------

    plot("today", Location, hourly_indices, hourly_labels, hourly_speeds, hourly_gust_speeds, today_end, tomorrow_start, tomorrow_end, date_titel, hourly_temp, hourly_rain, pop)
    plot("tomorrow", Location, hourly_indices, hourly_labels, hourly_speeds, hourly_gust_speeds, today_end, tomorrow_start, tomorrow_end, date_titel, hourly_temp, hourly_rain, pop)

def escape_markdown(text):
    return re.sub(r'([_\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

def create_message(data, hourly_rain):
    days_temp, daily_temp_feels, days_wind, days_gust, days_pop, day_dt, days_rain, days_description = extract_daily_data(data)
    uhrzeit_sunset = datetime.fromtimestamp(data["daily"][0]["sunset"]).strftime('%H:%M')
    uhrzeit_sunset_1 = datetime.fromtimestamp(data["daily"][1]["sunset"]).strftime('%H:%M')
    hour_sunset = datetime.fromtimestamp(data["daily"][0]["sunset"]).strftime('%H')
    hour_sunset_1 = datetime.fromtimestamp(data["daily"][1]["sunset"]).strftime('%H')
    count_windstamps = int(hour_sunset) - 8
    count_windstamps_1 = int(hour_sunset_1) - 8 + 24
    wind_speeds = []
    wind_speeds_1 = []
    wind_gust_speeds  = []
    wind_gust_speeds_1  = []
    pops  = []
    pops_1  = []
    rain = hourly_rain[:count_windstamps]
    rain_1 = hourly_rain[24:count_windstamps_1]
    for entry in data["hourly"][:count_windstamps]:  
        wind = entry.get("wind_speed", 0)
        wind_speeds.append(float(wind))
        wind_gust = entry.get("wind_gust", 0)
        wind_gust_speeds.append(float(wind_gust))
        pop = entry.get("pop", 0)
        pops.append(float(pop))
    for entry in data["hourly"][24:count_windstamps_1]:  
        wind_1 = entry.get("wind_speed", 0)
        wind_speeds_1.append(float(wind_1))
        wind_gust_1 = entry.get("wind_gust", 0)
        wind_gust_speeds_1.append(float(wind_gust_1))
        pop_1 = entry.get("pop", 0)
        pops_1.append(float(pop_1))         
         
    wind_max = wind_speed_to_beaufort(max(wind_speeds))
    wind_max_1 = wind_speed_to_beaufort(max(wind_speeds_1))
    wind_min = wind_speed_to_beaufort(min(wind_speeds))
    wind_min_1 = wind_speed_to_beaufort(min(wind_speeds_1))
    wind_gust_max = wind_speed_to_beaufort(max(wind_gust_speeds))
    wind_gust_max_1 = wind_speed_to_beaufort(max(wind_gust_speeds_1))
    wind_gust_min = wind_speed_to_beaufort(min(wind_gust_speeds))
    wind_gust_min_1 = wind_speed_to_beaufort(min(wind_gust_speeds_1))
    pop_max = max(pops)*100
    pop_max_1 = max(pops_1)*100
    fazit = segel_einschaetzung(daily_temp_feels[0],pop_max,wind_max,wind_gust_max,max(rain), 1)
    fazit_1 = segel_einschaetzung(daily_temp_feels[1],pop_max_1,wind_max_1,wind_gust_max_1,max(rain_1),1)

    fazit_week = []
    for i in range(len(days_temp)):
        fazit_week.append(segel_einschaetzung(days_temp[i], days_pop[i]*100, wind_speed_to_beaufort(days_wind[i]), wind_speed_to_beaufort(days_gust[i]),days_rain[i],2))
    wetter_heute = (
        f"🌤*Guten Morgen Berlin*\n\n"
        f"*heute ist {fazit}*\n\n"
        f"- Temp. Tag: {int(days_temp[0])}°C gefühlt {int(daily_temp_feels[0])}°C\n"
        f"- Wind: Min: {wind_min}bft Max: {wind_max}bft \n"
        f"- Böen: Min: {wind_gust_min}bft Max: {wind_gust_max}bft \n"
        f"- Regenwarscheinlichkeit: {pop_max}% \n"
        f"- Max. Regenmenge: {max(rain)}mm/h \n"
        f"- Beschreibung: {days_description[0]}\n"
        f"- Sonnenuntergang: {uhrzeit_sunset}\n\n"
        f"*Die Aussicht für morgen:*\n\n"
        f"*morgen ist {fazit_1}*\n\n"
        f"- Temp. Tag: {int(days_temp[1])}°C gefühlt {int(daily_temp_feels[1])}°C\n"
        f"- Wind: Min: {wind_min_1}bft Max: {wind_max_1}bft \n"
        f"- Böen: Min: {wind_gust_min_1}bft Max: {wind_gust_max_1}bft \n"
        f"- Regenwarscheinlichkeit: {pop_max_1}% \n"
        f"- Max. Regenmenge: {max(rain_1)}mm/h \n"
        f"- Beschreibung: {days_description[1]}\n"
        f"- Sonnenuntergang: {uhrzeit_sunset_1}\n\n"
        f"*Die Aussicht für die nächsten Tage:*\n\n"
        f"- *{convert_timestamp_to_berlin(day_dt[2]).strftime('%a, %d.%m.')}:* {fazit_week[2]}\n"
        f"- *{convert_timestamp_to_berlin(day_dt[3]).strftime('%a, %d.%m.')}:* {fazit_week[3]}\n"
        f"- *{convert_timestamp_to_berlin(day_dt[4]).strftime('%a, %d.%m.')}:* {fazit_week[4]}\n"
        f"- *{convert_timestamp_to_berlin(day_dt[5]).strftime('%a, %d.%m.')}:* {fazit_week[5]}\n"
        f"- *{convert_timestamp_to_berlin(day_dt[6]).strftime('%a, %d.%m.')}:* {fazit_week[6]}\n"
        f"- *{convert_timestamp_to_berlin(day_dt[7]).strftime('%a, %d.%m.')}:* {fazit_week[7]}\n"
    )
    return escape_markdown(wetter_heute), hour_sunset

def segel_einschaetzung(temp, pop, wind, gust, rain, level):
    #Level 1 = Ausführlicher Satz
    #Level 2 = Gekürzte erklärung
    #Level 3 = Nur Emojis
        if wind < 2:
            if level == 1:
                return " kein guter Tag – zu wenig Wind🌬️."
            if level == 2:
                return " zu wenig Wind.🌬️"
        if wind > 7:
            if level == 1:
                return " kein guter Tag – zu viel Wind🌬️."
            if level == 2:
                return " zu viel Wind.🌬️"
        if gust - wind > 6:
            if level == 1:
                return " Achtung geboten – starke Böen,💨 könnte gefährlich sein."
            if level == 2:
                return "⚠️ starke Böen.💨"
        if rain > 0.7:
            if pop > 60:
                if level == 1: 
                    return "die Regenmenge & Risiko zu hoch🌧️. Lieber abwarten."
                if level == 2: 
                    return "Regenrisiko hoch.🌧️"
        if temp < 15:
            if level == 1:
                return "🥶 kein guter Segeltag. Ziemlich kalt – nur was für Hartgesottene."
            if level == 2: 
                return "Ziemlich kalt.🥶"
        if wind > 1 and wind < 4:
            if level == 1:
                return "ein guter Segeltag Wind und Wetter passen.⛵\nGute Bedingungen für Gennacker"
            if level == 2: 
                return "guter Segeltag.⛵"
        if wind > 3 and wind < 7:
            if level == 1:
                return "ein guter Segeltag Wind und Wetter passen.⛵\nGute Bedingungen für Trapez"
            if level == 2: 
                return "guter Segeltag.⛵"
        if level == 2:
            return "guter Segeltag.⛵"
        return "ein guter Segeltag Wind und Wetter passen.⛵"

def release_to_community(LAT, LON, ID, Location):
    data = import_json(LAT, LON)
    
    hourly_wind, hourly_temp, pop, hourly_rain, hourly_gust = extract_hourly_data(data)
    message, hour_sunset=create_message(data, hourly_rain)
    plot_wind_speed(hourly_wind, hourly_gust, hourly_temp, pop, hourly_rain, hour_sunset, Location)
    send_telegram_message(bot_token, chat_id, message, ID)
    send_telegram_photo(ID,f"{Location}_wetter_heute.png","heute")
    send_telegram_photo(ID,f"{Location}_wetter_morgen.png","morgen")

def main():

    for location in config["locations"]:
        release_to_community(
        location["lat"],
        location["lon"],
        location["channel_id"],
        location["name"]
        )    

if __name__ == "__main__":
    main()