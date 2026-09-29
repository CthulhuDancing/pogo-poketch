"""CP-cap endpoint calculations for arbitrary Pokemon GO formats."""

from __future__ import annotations

from numbers import Real

from .cp import calculate_at_level, calculate_cp
from .shared.cpm import iter_levels, validate_level
from .shared.models import BaseStats, IVs, LeagueEndpoint


def _validate_cap(cap: int) -> int:
    if isinstance(cap, bool) or not isinstance(cap, int):
        raise TypeError("cap must be an integer")
    if cap < 1:
        raise ValueError("cap must be positive")
    return cap


def fits_cp_cap(cp: int, cap: int) -> bool:
    """Return whether a displayed CP value is legal under a CP cap."""
    _validate_cap(cap)
    if isinstance(cp, bool) or not isinstance(cp, int):
        raise TypeError("cp must be an integer")
    if cp < 0:
        raise ValueError("cp cannot be negative")
    return cp <= cap


def is_level_eligible(
    base_stats: BaseStats,
    ivs: IVs,
    level: Real,
    cap: int,
) -> bool:
    """Return whether a specific Pokemon build fits the supplied CP cap."""
    return fits_cp_cap(calculate_cp(base_stats, ivs, level), cap)


def find_league_endpoint(
    base_stats: BaseStats,
    ivs: IVs,
    cap: int,
    *,
    min_level: Real = 1.0,
    max_level: Real = 50.0,
) -> LeagueEndpoint | None:
    """Find the highest half-level that fits an arbitrary CP cap.

    Returns None when even min_level exceeds the cap. max_level is a mechanics
    boundary supplied by the caller: use 50 for normal powered Pokemon, 51 when
    intentionally evaluating a Best Buddy state, or another supported encoded
    level for a special deterministic context.
    """
    cap = _validate_cap(cap)
    low = validate_level(min_level)
    high = validate_level(max_level)
    if high < low:
        raise ValueError("max_level must be greater than or equal to min_level")

    for level in reversed(iter_levels(low, high)):
        calculation = calculate_at_level(base_stats, ivs, level)
        if calculation.cp <= cap:
            return LeagueEndpoint(
                cap=cap,
                level=level,
                cp=calculation.cp,
                headroom=cap - calculation.cp,
                stats=calculation.stats,
            )
    return None
