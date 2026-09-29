"""Strict input primitives and immutable calculation result models."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .constants import IV_MAX, IV_MIN


def _validate_int(name: str, value: int, minimum: int | None = None) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be at least {minimum}")


def _validate_iv(name: str, value: int) -> None:
    _validate_int(name, value)
    if not IV_MIN <= value <= IV_MAX:
        raise ValueError(f"{name} must be between {IV_MIN} and {IV_MAX}")


@dataclass(frozen=True, slots=True)
class BaseStats:
    attack: int
    defense: int
    stamina: int

    def __post_init__(self) -> None:
        _validate_int("attack", self.attack, 1)
        _validate_int("defense", self.defense, 1)
        _validate_int("stamina", self.stamina, 1)


@dataclass(frozen=True, slots=True)
class IVs:
    attack: int
    defense: int
    stamina: int

    def __post_init__(self) -> None:
        _validate_iv("attack IV", self.attack)
        _validate_iv("defense IV", self.defense)
        _validate_iv("stamina IV", self.stamina)


@dataclass(frozen=True, slots=True)
class EffectiveStats:
    attack: float
    defense: float
    stamina: float
    hp: int
    stat_product: float


@dataclass(frozen=True, slots=True)
class PokemonCalculation:
    level: float
    cpm: float
    cp: int
    stats: EffectiveStats


@dataclass(frozen=True, slots=True)
class LeagueEndpoint:
    cap: int
    level: float
    cp: int
    headroom: int
    stats: EffectiveStats


@dataclass(frozen=True, slots=True)
class IVRankEntry:
    ivs: IVs
    rank: int
    percentile: float
    candidate_count: int
    stat_product_percent: float
    endpoint: LeagueEndpoint


class PowerUpForm(str, Enum):
    NORMAL = "normal"
    SHADOW = "shadow"
    PURIFIED = "purified"


@dataclass(frozen=True, slots=True)
class PowerUpStepCost:
    level_from: float
    level_to: float
    stardust: int
    candy: int
    candy_xl: int
    form: PowerUpForm
    lucky: bool


@dataclass(frozen=True, slots=True)
class PowerUpCost:
    start_level: float
    target_level: float
    power_ups: int
    stardust: int
    candy: int
    candy_xl: int
    form: PowerUpForm
    lucky: bool
