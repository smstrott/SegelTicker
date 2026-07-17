from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Sequence, Tuple

from sailing_score import (
    DEFAULT_PROFILE,
    HourlyConditions,
    SailingProfile,
    WindowRating,
    category_for_score,
    evaluate_window,
)


@dataclass(frozen=True)
class ForecastHour:
    timestamp: datetime
    conditions: HourlyConditions


@dataclass(frozen=True)
class WindowCandidate:
    start_index: int
    end_index: int
    rating: WindowRating


@dataclass(frozen=True)
class SailingOpportunity:
    start: datetime
    end: datetime
    duration_hours: int
    score: int
    category: str
    reasons: Tuple[str, ...]


def evaluate_sailing_windows(
    forecast: Sequence[ForecastHour],
    profile: SailingProfile = DEFAULT_PROFILE,
) -> List[WindowCandidate]:
    window_size = profile.minimum_window_hours
    candidates = []
    for start_index in range(len(forecast) - window_size + 1):
        end_index = start_index + window_size
        rating = evaluate_window(
            [hour.conditions for hour in forecast[start_index:end_index]],
            profile,
        )
        candidates.append(WindowCandidate(start_index, end_index, rating))
    return candidates


def _unique_reasons(candidates: Sequence[WindowCandidate]) -> Tuple[str, ...]:
    return tuple(
        dict.fromkeys(
            reason
            for candidate in candidates
            for reason in candidate.rating.reasons
        )
    )


def find_sailing_opportunities(
    forecast: Sequence[ForecastHour],
    profile: SailingProfile = DEFAULT_PROFILE,
) -> List[SailingOpportunity]:
    candidates = [
        candidate
        for candidate in evaluate_sailing_windows(forecast, profile)
        if candidate.rating.suitable
    ]
    if not candidates:
        return []

    groups: List[List[WindowCandidate]] = [[candidates[0]]]
    for candidate in candidates[1:]:
        previous = groups[-1][-1]
        if candidate.start_index == previous.start_index + 1:
            groups[-1].append(candidate)
        else:
            groups.append([candidate])

    opportunities = []
    for group in groups:
        start_index = group[0].start_index
        end_index = group[-1].end_index
        score = round(sum(item.rating.score for item in group) / len(group))
        opportunities.append(
            SailingOpportunity(
                start=forecast[start_index].timestamp,
                end=forecast[end_index - 1].timestamp + timedelta(hours=1),
                duration_hours=end_index - start_index,
                score=score,
                category=category_for_score(score),
                reasons=_unique_reasons(group),
            )
        )
    return opportunities


def find_best_sailing_opportunity(
    forecast: Sequence[ForecastHour],
    profile: SailingProfile = DEFAULT_PROFILE,
) -> Optional[SailingOpportunity]:
    opportunities = find_sailing_opportunities(forecast, profile)
    if not opportunities:
        return None

    return max(
        opportunities,
        key=lambda opportunity: (
            opportunity.score // 5,
            opportunity.duration_hours,
            opportunity.score,
            -opportunity.start.timestamp(),
        ),
    )
