"""Combat Power calculations for Pokemon GO."""

from __future__ import annotations

import math
from numbers import Real

from .shared.constants import CP_MIN
from .shared.cpm import get_cpm, validate_level
from .shared.models import BaseStats, IVs, PokemonCalculation
from .stats import calculate_effective_stats


def calculate_cp(base_stats: BaseStats, ivs: IVs, level: Real) -> int:
    """Calculate displayed CP using the standard Pokemon GO CP formula."""
    cpm = get_cpm(level)
    attack = base_stats.attack + ivs.attack
    defense = base_stats.defense + ivs.defense
    stamina = base_stats.stamina + ivs.stamina
    raw_cp = (
        attack
        * math.sqrt(defense)
        * math.sqrt(stamina)
        * (cpm**2)
        / 10.0
    )
    return max(CP_MIN, math.floor(raw_cp))


def calculate_at_level(
    base_stats: BaseStats,
    ivs: IVs,
    level: Real,
) -> PokemonCalculation:
    """Return CP and effective stats together for one level."""
    canonical_level = validate_level(level)
    return PokemonCalculation(
        level=canonical_level,
        cpm=get_cpm(canonical_level),
        cp=calculate_cp(base_stats, ivs, canonical_level),
        stats=calculate_effective_stats(base_stats, ivs, canonical_level),
    )
