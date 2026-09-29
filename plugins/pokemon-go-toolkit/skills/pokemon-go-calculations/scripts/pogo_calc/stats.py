"""Effective-stat calculations for Pokemon GO."""

from __future__ import annotations

import math
from numbers import Real

from .shared.constants import CP_MIN
from .shared.cpm import get_cpm
from .shared.models import BaseStats, EffectiveStats, IVs


def calculate_effective_stats(
    base_stats: BaseStats,
    ivs: IVs,
    level: Real,
) -> EffectiveStats:
    """Calculate effective Attack, Defense, Stamina, battle HP, and stat product.

    Attack, Defense, and Stamina retain their unrounded effective values. Battle
    HP is floored and has the game's minimum of 10. Stat product uses actual
    battle HP: effective Attack * effective Defense * floored HP.
    """
    cpm = get_cpm(level)
    attack = (base_stats.attack + ivs.attack) * cpm
    defense = (base_stats.defense + ivs.defense) * cpm
    stamina = (base_stats.stamina + ivs.stamina) * cpm
    hp = max(CP_MIN, math.floor(stamina))
    stat_product = attack * defense * hp
    return EffectiveStats(
        attack=attack,
        defense=defense,
        stamina=stamina,
        hp=hp,
        stat_product=stat_product,
    )
