from dataclasses import dataclass
from typing import Sequence, Tuple


@dataclass(frozen=True)
class SailingProfile:
    minimum_window_hours: int = 3
    ideal_wind_min_bft: int = 3
    ideal_wind_max_bft: int = 5
    sailable_wind_min_bft: int = 2
    sailable_wind_max_bft: int = 6
    ideal_gust_difference_bft: int = 1
    maximum_gust_difference_bft: int = 2
    ideal_rain_probability: float = 0.30
    maximum_rain_probability: float = 0.60
    ideal_rain_mm: float = 0.20
    maximum_rain_mm: float = 0.70
    ideal_temperature_c: float = 18
    minimum_temperature_c: float = 15


@dataclass(frozen=True)
class HourlyConditions:
    wind_bft: int
    gust_bft: int
    rain_probability: float
    rain_mm: float
    temperature_c: float


@dataclass(frozen=True)
class WindowRating:
    score: int
    category: str
    suitable: bool
    reasons: Tuple[str, ...]


DEFAULT_PROFILE = SailingProfile()

WEIGHTS = {
    "wind": 0.35,
    "gust": 0.30,
    "rain_probability": 0.10,
    "rain_amount": 0.15,
    "temperature": 0.10,
}


def _level(value, ideal, acceptable):
    if ideal(value):
        return 100
    if acceptable(value):
        return 60
    return 0


def _hour_score(hour: HourlyConditions, profile: SailingProfile) -> float:
    gust_difference = max(0, hour.gust_bft - hour.wind_bft)
    component_scores = {
        "wind": _level(
            hour.wind_bft,
            lambda value: profile.ideal_wind_min_bft <= value <= profile.ideal_wind_max_bft,
            lambda value: profile.sailable_wind_min_bft <= value <= profile.sailable_wind_max_bft,
        ),
        "gust": _level(
            gust_difference,
            lambda value: value <= profile.ideal_gust_difference_bft,
            lambda value: value <= profile.maximum_gust_difference_bft,
        ),
        "rain_probability": _level(
            hour.rain_probability,
            lambda value: value < profile.ideal_rain_probability,
            lambda value: value <= profile.maximum_rain_probability,
        ),
        "rain_amount": _level(
            hour.rain_mm,
            lambda value: value < profile.ideal_rain_mm,
            lambda value: value <= profile.maximum_rain_mm,
        ),
        "temperature": _level(
            hour.temperature_c,
            lambda value: value >= profile.ideal_temperature_c,
            lambda value: value >= profile.minimum_temperature_c,
        ),
    }
    return sum(component_scores[name] * weight for name, weight in WEIGHTS.items())


def _critical_reasons(
    hours: Sequence[HourlyConditions], profile: SailingProfile
) -> Tuple[str, ...]:
    reasons = []
    if any(hour.wind_bft < profile.sailable_wind_min_bft for hour in hours):
        reasons.append("zeitweise zu wenig Wind")
    if any(hour.wind_bft > profile.sailable_wind_max_bft for hour in hours):
        reasons.append("zeitweise zu viel Wind")
    if any(
        hour.gust_bft - hour.wind_bft > profile.maximum_gust_difference_bft
        for hour in hours
    ):
        reasons.append("zu starke Böen")
    if any(hour.rain_probability > profile.maximum_rain_probability for hour in hours):
        reasons.append("hohes Regenrisiko")
    if any(hour.rain_mm > profile.maximum_rain_mm for hour in hours):
        reasons.append("zu hohe Regenmenge")
    return tuple(reasons)


def _comfort_reasons(
    hours: Sequence[HourlyConditions], profile: SailingProfile
) -> Tuple[str, ...]:
    reasons = []
    if any(hour.temperature_c < profile.minimum_temperature_c for hour in hours):
        reasons.append("kühl")
    if any(
        hour.wind_bft not in range(profile.ideal_wind_min_bft, profile.ideal_wind_max_bft + 1)
        for hour in hours
    ):
        reasons.append("Wind nicht durchgehend im Idealbereich")
    return tuple(reasons)


def category_for_score(score: int) -> str:
    if score >= 85:
        return "ausgezeichnet"
    if score >= 70:
        return "gut"
    if score >= 50:
        return "eingeschränkt"
    return "ungeeignet"


def evaluate_window(
    hours: Sequence[HourlyConditions], profile: SailingProfile = DEFAULT_PROFILE
) -> WindowRating:
    if len(hours) < profile.minimum_window_hours:
        raise ValueError(
            f"Ein Segelfenster benötigt mindestens {profile.minimum_window_hours} Stunden."
        )

    hourly_scores = [_hour_score(hour, profile) for hour in hours]
    average_score = sum(hourly_scores) / len(hourly_scores)
    score = round(average_score * 0.6 + min(hourly_scores) * 0.4)

    critical_reasons = _critical_reasons(hours, profile)
    if critical_reasons:
        score = min(score, 49)

    reasons = critical_reasons or _comfort_reasons(hours, profile)
    return WindowRating(
        score=score,
        category=category_for_score(score),
        suitable=not critical_reasons and score >= 50,
        reasons=reasons,
    )
