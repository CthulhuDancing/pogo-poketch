"""Deterministic Pokemon GO Pokestop Showcase score calculations.

The scoring model implemented here is the community reverse-engineered
species-relative "Biggest" model:

    height: 800 * (height / mean_height) / xxl_height_class
    weight: 150 * (weight / mean_weight) / (xxl_height_class + 0.5)
    IVs:    50 * iv_sum / 45
    XXL:    +178 when the specimen is classified XXL

Displayed in-game height and weight are rounded, so callers can either score
exact measurements or calculate a deterministic interval around displayed
measurements.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation


HEIGHT_POINTS = Decimal("800")
WEIGHT_POINTS = Decimal("150")
IV_POINTS = Decimal("50")
XXL_BONUS = Decimal("178")
MAX_IV_SUM = 45
SUPPORTED_XXL_CLASSES = (
    Decimal("1.55"),
    Decimal("1.75"),
    Decimal("2.00"),
)


def _decimal(name: str, value: int | float | str | Decimal) -> Decimal:
    if isinstance(value, bool):
        raise TypeError(f"{name} must be numeric")
    try:
        result = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise TypeError(f"{name} must be numeric") from exc
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def _positive(name: str, value: int | float | str | Decimal) -> Decimal:
    result = _decimal(name, value)
    if result <= 0:
        raise ValueError(f"{name} must be greater than 0")
    return result


def _validate_iv_sum(value: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("iv_sum must be an integer")
    if not 0 <= value <= MAX_IV_SUM:
        raise ValueError("iv_sum must be between 0 and 45")
    return value


def _validate_xxl_class(value: int | float | str | Decimal) -> Decimal:
    result = _decimal("xxl_height_class", value)
    if result not in SUPPORTED_XXL_CLASSES:
        allowed = ", ".join(str(item) for item in SUPPORTED_XXL_CLASSES)
        raise ValueError(f"xxl_height_class must be one of: {allowed}")
    return result


@dataclass(frozen=True, slots=True)
class ShowcaseComponents:
    height_points: float
    weight_points: float
    iv_points: float
    xxl_bonus: float
    total: float


@dataclass(frozen=True, slots=True)
class ShowcaseScoreRange:
    minimum: ShowcaseComponents
    estimate: ShowcaseComponents
    maximum: ShowcaseComponents
    height_interval_m: tuple[float, float]
    weight_interval_kg: tuple[float, float]
    height_resolution_m: float
    weight_resolution_kg: float


def _score_decimal(
    *,
    height_m: Decimal,
    weight_kg: Decimal,
    mean_height_m: Decimal,
    mean_weight_kg: Decimal,
    xxl_height_class: Decimal,
    iv_sum: int,
    is_xxl: bool,
) -> tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
    height_points = HEIGHT_POINTS * (height_m / mean_height_m) / xxl_height_class
    weight_class = xxl_height_class + Decimal("0.5")
    weight_points = WEIGHT_POINTS * (weight_kg / mean_weight_kg) / weight_class
    iv_points = IV_POINTS * Decimal(iv_sum) / Decimal(MAX_IV_SUM)
    xxl_bonus = XXL_BONUS if is_xxl else Decimal("0")
    total = height_points + weight_points + iv_points + xxl_bonus
    return height_points, weight_points, iv_points, xxl_bonus, total


def calculate_showcase_score(
    *,
    height_m: int | float | str | Decimal,
    weight_kg: int | float | str | Decimal,
    mean_height_m: int | float | str | Decimal,
    mean_weight_kg: int | float | str | Decimal,
    xxl_height_class: int | float | str | Decimal,
    iv_sum: int,
    is_xxl: bool,
) -> ShowcaseComponents:
    """Calculate one score from exact height and weight inputs."""

    if not isinstance(is_xxl, bool):
        raise TypeError("is_xxl must be a boolean")

    h = _positive("height_m", height_m)
    w = _positive("weight_kg", weight_kg)
    mean_h = _positive("mean_height_m", mean_height_m)
    mean_w = _positive("mean_weight_kg", mean_weight_kg)
    xxl_class = _validate_xxl_class(xxl_height_class)
    ivs = _validate_iv_sum(iv_sum)

    height_points, weight_points, iv_points, bonus, total = _score_decimal(
        height_m=h,
        weight_kg=w,
        mean_height_m=mean_h,
        mean_weight_kg=mean_w,
        xxl_height_class=xxl_class,
        iv_sum=ivs,
        is_xxl=is_xxl,
    )

    return ShowcaseComponents(
        height_points=float(height_points),
        weight_points=float(weight_points),
        iv_points=float(iv_points),
        xxl_bonus=float(bonus),
        total=float(total),
    )


def calculate_displayed_showcase_range(
    *,
    displayed_height_m: int | float | str | Decimal,
    displayed_weight_kg: int | float | str | Decimal,
    mean_height_m: int | float | str | Decimal,
    mean_weight_kg: int | float | str | Decimal,
    xxl_height_class: int | float | str | Decimal,
    iv_sum: int,
    is_xxl: bool,
    height_resolution_m: int | float | str | Decimal = Decimal("0.01"),
    weight_resolution_kg: int | float | str | Decimal = Decimal("0.01"),
) -> ShowcaseScoreRange:
    """Estimate a score interval from rounded in-game measurements.

    The displayed measurement is treated as a nearest-resolution rounded value,
    so its underlying value is bounded by +/- half of the supplied resolution.
    The scoring model is monotonic in both height and weight, making the score
    extrema occur at the corresponding measurement bounds.
    """

    display_h = _positive("displayed_height_m", displayed_height_m)
    display_w = _positive("displayed_weight_kg", displayed_weight_kg)
    height_res = _positive("height_resolution_m", height_resolution_m)
    weight_res = _positive("weight_resolution_kg", weight_resolution_kg)

    half_h = height_res / Decimal("2")
    half_w = weight_res / Decimal("2")
    min_h = max(Decimal("0"), display_h - half_h)
    max_h = display_h + half_h
    min_w = max(Decimal("0"), display_w - half_w)
    max_w = display_w + half_w

    common = {
        "mean_height_m": mean_height_m,
        "mean_weight_kg": mean_weight_kg,
        "xxl_height_class": xxl_height_class,
        "iv_sum": iv_sum,
        "is_xxl": is_xxl,
    }

    minimum = calculate_showcase_score(height_m=min_h, weight_kg=min_w, **common)
    estimate = calculate_showcase_score(height_m=display_h, weight_kg=display_w, **common)
    maximum = calculate_showcase_score(height_m=max_h, weight_kg=max_w, **common)

    return ShowcaseScoreRange(
        minimum=minimum,
        estimate=estimate,
        maximum=maximum,
        height_interval_m=(float(min_h), float(max_h)),
        weight_interval_kg=(float(min_w), float(max_w)),
        height_resolution_m=float(height_res),
        weight_resolution_kg=float(weight_res),
    )
