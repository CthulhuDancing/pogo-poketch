"""Stat-product IV ranking under an arbitrary CP cap."""

from __future__ import annotations

from itertools import product
from numbers import Real

from .league import find_league_endpoint
from .shared.constants import IV_MAX, IV_MIN
from .shared.models import BaseStats, IVRankEntry, IVs, LeagueEndpoint


def _validate_iv_bound(name: str, value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if not IV_MIN <= value <= IV_MAX:
        raise ValueError(f"{name} must be between {IV_MIN} and {IV_MAX}")
    return value


def _ranking_key(item: tuple[IVs, LeagueEndpoint]) -> tuple[float, ...]:
    ivs, endpoint = item
    stats = endpoint.stats
    # Stat product is authoritative. Remaining fields only make exact ties
    # deterministic; they do not alter non-tied stat-product ordering.
    return (
        -stats.stat_product,
        -stats.defense,
        -stats.hp,
        -stats.attack,
        -endpoint.level,
        ivs.attack,
        -ivs.defense,
        -ivs.stamina,
    )


def rank_all_iv_spreads(
    base_stats: BaseStats,
    cap: int,
    *,
    min_level: Real = 1.0,
    max_level: Real = 50.0,
    iv_floor: int = 0,
    iv_ceiling: int = 15,
) -> tuple[IVRankEntry, ...]:
    """Rank every IV spread in the requested uniform IV range by stat product.

    Ranking is 1-based. Exact stat-product ties are made deterministic by bulk,
    Attack, level, then IV values. Percentile maps rank 1 to 100 and the final
    candidate to 0. stat_product_percent is relative to the rank-1 result.
    """
    floor = _validate_iv_bound("iv_floor", iv_floor)
    ceiling = _validate_iv_bound("iv_ceiling", iv_ceiling)
    if ceiling < floor:
        raise ValueError("iv_ceiling must be greater than or equal to iv_floor")

    candidates: list[tuple[IVs, LeagueEndpoint]] = []
    for attack, defense, stamina in product(range(floor, ceiling + 1), repeat=3):
        ivs = IVs(attack, defense, stamina)
        endpoint = find_league_endpoint(
            base_stats,
            ivs,
            cap,
            min_level=min_level,
            max_level=max_level,
        )
        if endpoint is not None:
            candidates.append((ivs, endpoint))

    candidates.sort(key=_ranking_key)
    if not candidates:
        return ()

    count = len(candidates)
    best_stat_product = candidates[0][1].stats.stat_product
    results: list[IVRankEntry] = []
    for index, (ivs, endpoint) in enumerate(candidates, start=1):
        percentile = 100.0 if count == 1 else 100.0 * (count - index) / (count - 1)
        stat_product_percent = 100.0 * endpoint.stats.stat_product / best_stat_product
        results.append(
            IVRankEntry(
                ivs=ivs,
                rank=index,
                percentile=percentile,
                candidate_count=count,
                stat_product_percent=stat_product_percent,
                endpoint=endpoint,
            )
        )
    return tuple(results)


def rank_iv_spread(
    base_stats: BaseStats,
    ivs: IVs,
    cap: int,
    *,
    min_level: Real = 1.0,
    max_level: Real = 50.0,
    iv_floor: int = 0,
    iv_ceiling: int = 15,
) -> IVRankEntry | None:
    """Return the rank entry for one IV spread within the requested IV pool.

    Returns None if the IVs are outside the requested pool or cannot fit the cap
    at min_level.
    """
    floor = _validate_iv_bound("iv_floor", iv_floor)
    ceiling = _validate_iv_bound("iv_ceiling", iv_ceiling)
    if ceiling < floor:
        raise ValueError("iv_ceiling must be greater than or equal to iv_floor")
    if not (
        floor <= ivs.attack <= ceiling
        and floor <= ivs.defense <= ceiling
        and floor <= ivs.stamina <= ceiling
    ):
        return None

    for entry in rank_all_iv_spreads(
        base_stats,
        cap,
        min_level=min_level,
        max_level=max_level,
        iv_floor=floor,
        iv_ceiling=ceiling,
    ):
        if entry.ivs == ivs:
            return entry
    return None
