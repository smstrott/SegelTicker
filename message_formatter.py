import re

from weather_analysis import (
    best_sailing_window,
    convert_timestamp_to_berlin,
    sailing_forecast_for_day,
    wind_speed_to_beaufort,
)


def escape_markdown(text):
    return re.sub(r'([_\[\]()~`>#+\-=|{}.!])', r'\\\1', text)


def format_sailing_window(opportunity):
    if opportunity is None:
        return "Kein stabiles Segelfenster von mindestens 3 Stunden"
    return (
        f"{opportunity.start.strftime('%H:%M')}–"
        f"{opportunity.end.strftime('%H:%M')} Uhr "
        f"({opportunity.duration_hours} Std., {opportunity.category}, "
        f"{opportunity.score}/100)"
    )


def format_sailing_assessment(opportunity):
    if opportunity is None:
        return "kein geeignetes Segelfenster"
    return {
        "ausgezeichnet": "ausgezeichnete Segelbedingungen",
        "gut": "gute Segelbedingungen",
        "eingeschränkt": "eingeschränkt geeignete Segelbedingungen",
    }[opportunity.category]


def format_sailing_reasons(opportunity):
    if opportunity is None:
        return "Die Bedingungen sind nicht mindestens 3 Stunden stabil geeignet."
    if not opportunity.reasons:
        return "Wind und Wetter sind in diesem Zeitraum stabil."
    return "Hinweis: " + ", ".join(opportunity.reasons) + "."


def compass_direction(degrees):
    names = ("Nord", "Nordost", "Ost", "Südost", "Süd", "Südwest", "West", "Nordwest")
    return names[round(degrees / 45) % 8]


def format_day_message(data, daily_index, heading):
    forecast = sailing_forecast_for_day(data, daily_index)
    opportunity = best_sailing_window(data, daily_index)
    if not forecast:
        raise ValueError(f"Keine stündlichen Daten für {heading} vorhanden")

    conditions = [hour.conditions for hour in forecast]
    timestamps = {hour.timestamp for hour in forecast}
    directions = [
        compass_direction(float(entry.get("wind_deg", 0)))
        for entry in data["hourly"]
        if convert_timestamp_to_berlin(entry["dt"]) in timestamps
    ]
    direction_text = directions[0]
    if directions[-1] != directions[0]:
        direction_text += f", später {directions[-1]}"

    maximum_pop = round(max(item.rain_probability for item in conditions) * 100)
    maximum_rain = max(item.rain_mm for item in conditions)
    rain_text = "☀️ Trocken"
    if maximum_pop >= 10 or maximum_rain > 0:
        rain_text = f"🌧 Regenrisiko bis {maximum_pop} %, max. {maximum_rain:g} mm/h"

    window_text = "kein stabiles 3-Stunden-Fenster"
    if opportunity:
        window_text = f"{opportunity.start.strftime('%H:%M')}–{opportunity.end.strftime('%H:%M')} Uhr"

    reasons = ""
    if opportunity and opportunity.reasons:
        reasons = f"\nℹ️ {', '.join(opportunity.reasons)}"

    sunset = convert_timestamp_to_berlin(data["daily"][daily_index]["sunset"])
    return (
        f"*{heading}: {format_sailing_assessment(opportunity)}*\n"
        f"🕐 Bestes Fenster: *{window_text}*\n"
        f"🌬 Wind: {min(item.wind_bft for item in conditions)}–{max(item.wind_bft for item in conditions)} Bft, "
        f"Böen bis {max(item.gust_bft for item in conditions)} Bft\n"
        f"🧭 Richtung: {direction_text}\n"
        f"🌡 Temperatur: {round(min(item.temperature_c for item in conditions))}–"
        f"{round(max(item.temperature_c for item in conditions))} °C\n"
        f"{rain_text} · Sonnenuntergang {sunset.strftime('%H:%M')}{reasons}"
    )


def format_daily_outlook(day):
    wind = wind_speed_to_beaufort(float(day.get("wind_speed", 0)))
    gust = wind_speed_to_beaufort(float(day.get("wind_gust", 0)))
    temperature = round(float(day.get("temp", {}).get("day", 0)))
    rain_probability = round(float(day.get("pop", 0)) * 100)
    rain_amount = float(day.get("rain", 0))

    if wind < 2:
        tendency = "🌬 zu wenig Wind"
    elif wind > 6:
        tendency = "⚠️ zu viel Wind"
    elif gust - wind > 2:
        tendency = "⚠️ stark böig"
    elif rain_probability > 60 or rain_amount > 1.7:
        tendency = "🌧 regnerisch"
    elif temperature < 15:
        tendency = "🥶 kühl"
    else:
        tendency = "⛵ gute Tendenz"

    details = f"{wind} Bft, Böen {gust} · {temperature} °C"
    if rain_probability >= 30 or rain_amount > 0:
        details += f" · Regen {rain_probability} %"
    return f"{tendency} · {details}"


def create_message(data, location):
    outlook_lines = "\n".join(
        f"• *{convert_timestamp_to_berlin(data['daily'][index]['dt']).strftime('%a, %d.%m.')}:* "
        f"{format_daily_outlook(data['daily'][index])}"
        for index in range(2, min(8, len(data["daily"])))
    )
    message = (
        f"⛵ *{location} · SegelTicker*\n\n"
        f"{format_day_message(data, 0, 'Heute')}\n\n"
        f"{format_day_message(data, 1, 'Morgen')}\n\n"
        f"*Weitere Aussichten*\n{outlook_lines}"
    )
    return escape_markdown(message)
