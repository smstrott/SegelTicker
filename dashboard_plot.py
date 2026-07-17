import math
from datetime import timedelta

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pytz

from message_formatter import format_sailing_assessment
from weather_analysis import (
    best_sailing_window,
    convert_timestamp_to_berlin,
    sailing_windows_for_day,
)


COLORS = {
    "navy": "#12355B",
    "blue": "#2F80ED",
    "temperature": "#E05A47",
    "rain": "#4AA3A2",
    "highlight": "#DDF4E4",
    "grid": "#D9E2EA",
    "text": "#183042",
}


def temperature_axis_max(temperatures):
    default_max = 35
    highest_temperature = max(temperatures, default=default_max)
    if highest_temperature <= default_max:
        return default_max
    return math.ceil(highest_temperature / 5) * 5


def smooth_hourly_series(timestamps, values, steps_per_hour=12):
    if len(timestamps) < 2:
        return list(timestamps), list(values)

    smooth_timestamps = []
    smooth_values = []
    for index in range(len(timestamps) - 1):
        start_time = timestamps[index]
        time_delta = timestamps[index + 1] - start_time
        start_value = values[index]
        value_delta = values[index + 1] - start_value
        for step in range(steps_per_hour):
            progress = step / steps_per_hour
            eased_progress = progress * progress * (3 - 2 * progress)
            smooth_timestamps.append(start_time + time_delta * progress)
            smooth_values.append(start_value + value_delta * eased_progress)

    smooth_timestamps.append(timestamps[-1])
    smooth_values.append(values[-1])
    return smooth_timestamps, smooth_values


def _highlight_sailing_windows(axes, opportunities, best_opportunity):
    for axis in axes:
        for opportunity in opportunities:
            axis.axvspan(
                opportunity.start,
                opportunity.end,
                color=COLORS["highlight"],
                alpha=0.40,
                linewidth=0,
            )
        if best_opportunity:
            axis.axvspan(
                best_opportunity.start,
                best_opportunity.end,
                color=COLORS["highlight"],
                alpha=0.55,
                linewidth=0,
            )


def plot_dashboard(data, day_index, location, hourly_wind, hourly_gust, hourly_temp, pop, hourly_rain):
    hourly_speeds, hourly_timestamps = zip(*hourly_wind)
    hourly_gust_speeds, _ = zip(*hourly_gust)
    timestamps = [convert_timestamp_to_berlin(value) for value in hourly_timestamps]
    sunset = convert_timestamp_to_berlin(data["daily"][day_index]["sunset"])
    range_start = sunset.replace(hour=8, minute=0, second=0, microsecond=0)
    range_end = sunset + timedelta(hours=2)
    indices = [
        index
        for index, timestamp in enumerate(timestamps)
        if range_start <= timestamp < range_end
    ]
    if not indices:
        raise ValueError(f"Keine stündlichen Daten für {range_start.date()} vorhanden")

    shown_times = [timestamps[index] for index in indices]
    shown_wind = [hourly_speeds[index] for index in indices]
    shown_gust = [hourly_gust_speeds[index] for index in indices]
    shown_temp = [hourly_temp[index] for index in indices]
    shown_pop = [pop[index] * 100 for index in indices]
    shown_rain = [hourly_rain[index] for index in indices]
    shown_direction = [float(data["hourly"][index].get("wind_deg", 0)) for index in indices]
    opportunities = sailing_windows_for_day(data, day_index)
    best_opportunity = best_sailing_window(data, day_index)
    has_relevant_rain = max(shown_pop, default=0) >= 10 or any(shown_rain)
    smooth_times, smooth_wind = smooth_hourly_series(shown_times, shown_wind)
    _, smooth_gust = smooth_hourly_series(shown_times, shown_gust)

    fig, (wind_ax, temp_ax, rain_ax) = plt.subplots(
        3,
        1,
        figsize=(10, 7),
        sharex=True,
        gridspec_kw={
            "height_ratios": [3.4, 1.2, 1.4 if has_relevant_rain else 0.55],
            "hspace": 0.12,
        },
    )
    fig.patch.set_facecolor("#F7FAFC")
    axes = (wind_ax, temp_ax, rain_ax)
    for axis in axes:
        axis.set_facecolor("white")
        axis.grid(axis="y", color=COLORS["grid"], linewidth=0.8, alpha=0.8)
        axis.spines[["top", "right"]].set_visible(False)
        axis.spines[["left", "bottom"]].set_color(COLORS["grid"])
        axis.tick_params(colors=COLORS["text"])
    _highlight_sailing_windows(axes, opportunities, best_opportunity)

    wind_ax.plot(smooth_times, smooth_gust, color=COLORS["blue"], linewidth=2, linestyle="--", label="Böen")
    wind_ax.plot(smooth_times, smooth_wind, color=COLORS["navy"], linewidth=3, label="Wind")
    wind_ax.plot(shown_times, shown_wind, color=COLORS["navy"], linestyle="none", marker="o", markersize=4)
    wind_ax.fill_between(smooth_times, smooth_wind, smooth_gust, color=COLORS["blue"], alpha=0.10)
    wind_ax.set_ylabel("Wind · Bft", color=COLORS["text"], fontweight="bold")
    wind_ax.set_ylim(0, max(8, math.ceil(max(shown_gust) + 1)))
    wind_ax.legend(loc="upper left", frameon=False, ncol=2)
    for timestamp, direction in zip(shown_times, shown_direction):
        wind_ax.text(
            timestamp,
            0.38,
            "↑",
            rotation=-direction,
            ha="center",
            va="center",
            fontsize=14,
            fontweight="bold",
            color=COLORS["navy"],
        )

    temp_ax.plot(shown_times, shown_temp, color=COLORS["temperature"], linewidth=2.5)
    temp_ax.set_ylabel("Temp. · °C", color=COLORS["temperature"], fontweight="bold")
    temperature_max = temperature_axis_max(shown_temp)
    temp_ax.set_ylim(0, temperature_max)
    temp_ax.set_yticks(range(0, temperature_max + 1, 10))

    if has_relevant_rain:
        rain_ax.bar(shown_times, shown_pop, width=0.025, color=COLORS["rain"], alpha=0.45)
        rain_ax.set_ylabel("Regen · %", color=COLORS["rain"], fontweight="bold")
        rain_ax.set_ylim(0, 100)
        maximum_rain = max(shown_rain, default=0)
        if maximum_rain > 0:
            rain_ax.text(
                0.99,
                0.88,
                f"Max. Regenmenge: {maximum_rain:g} mm/h",
                transform=rain_ax.transAxes,
                ha="right",
                va="top",
                fontsize=8.5,
                color=COLORS["blue"],
                fontweight="bold",
            )
    else:
        rain_ax.grid(False)
        rain_ax.set_yticks([])
        rain_ax.spines[["left", "right", "top"]].set_visible(False)
        rain_ax.text(
            0.01,
            0.5,
            "☀  Trocken · Regenrisiko unter 10 %",
            transform=rain_ax.transAxes,
            ha="left",
            va="center",
            color=COLORS["rain"],
            fontweight="bold",
        )

    for axis in axes:
        axis.axvline(sunset, color="#E6A23C", linewidth=1.4, linestyle=":", alpha=0.9)
    wind_ax.annotate(
        f"☀ {sunset.strftime('%H:%M')}",
        xy=(sunset, 1),
        xycoords=("data", "axes fraction"),
        xytext=(5, -5),
        textcoords="offset points",
        ha="left",
        va="top",
        fontsize=8.5,
        color="#A56613",
    )

    date_label = shown_times[0].strftime("%a, %d.%m.")
    assessment = format_sailing_assessment(best_opportunity).upper()
    fig.text(0.08, 0.965, f"{location.upper()} · {date_label}", fontsize=17, fontweight="bold", color=COLORS["text"], va="top")
    fig.text(0.08, 0.925, assessment, fontsize=12, fontweight="bold", color="#238455" if best_opportunity else "#B54747", va="top")
    fig.text(0.08, 0.895, f"Wind {min(shown_wind)}–{max(shown_wind)} Bft · Böen bis {max(shown_gust)} Bft", fontsize=9.5, color=COLORS["text"], va="top")
    if best_opportunity:
        dashboard_window = (
            f"{best_opportunity.start.strftime('%H:%M')}–{best_opportunity.end.strftime('%H:%M')} Uhr "
            f"· {best_opportunity.duration_hours} Std. · Score {best_opportunity.score}"
        )
    else:
        dashboard_window = "Kein geeignetes 3-Stunden-Fenster"
    fig.text(0.92, 0.925, dashboard_window, fontsize=10, color=COLORS["text"], ha="right", va="top")
    if len(opportunities) > 1:
        fig.text(0.92, 0.895, "Hellgrün: weitere geeignete Fenster", fontsize=8.5, color="#517466", ha="right", va="top")

    berlin_timezone = pytz.timezone("Europe/Berlin")
    rain_ax.xaxis.set_major_locator(mdates.HourLocator(interval=2, tz=berlin_timezone))
    rain_ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M", tz=berlin_timezone))
    rain_ax.set_xlabel("Uhrzeit", color=COLORS["text"], fontweight="bold")
    rain_ax.set_xlim(shown_times[0] - timedelta(minutes=20), shown_times[-1] + timedelta(hours=1))
    fig.subplots_adjust(top=0.84, left=0.10, right=0.92, bottom=0.10)

    file_end = "heute" if day_index == 0 else "morgen"
    plt.savefig(
        f"{location}_wetter_{file_end}.png",
        dpi=300,
        bbox_inches="tight",
        facecolor=fig.get_facecolor(),
    )
    plt.close(fig)


def plot_wind_speed(data, hourly_wind, hourly_gust, hourly_temp, pop, hourly_rain, location):
    plot_dashboard(data, 0, location, hourly_wind, hourly_gust, hourly_temp, pop, hourly_rain)
    plot_dashboard(data, 1, location, hourly_wind, hourly_gust, hourly_temp, pop, hourly_rain)
