"""Generic Pokemon GO power-up resource calculations."""

from __future__ import annotations

from numbers import Real

from .shared.constants import MAX_POWER_UP_LEVEL
from .shared.cpm import iter_levels, validate_level
from .shared.models import PowerUpCost, PowerUpForm, PowerUpStepCost

# Inclusive level bands. Costs are paid to move FROM a level to the next
# half-level. From level 40 onward, the candy field is Candy XL.
_COST_BANDS: tuple[tuple[float, float, int, int, int], ...] = (
    (1.0, 2.5, 200, 1, 0),
    (3.0, 4.5, 400, 1, 0),
    (5.0, 6.5, 600, 1, 0),
    (7.0, 8.5, 800, 1, 0),
    (9.0, 10.5, 1000, 1, 0),
    (11.0, 12.5, 1300, 2, 0),
    (13.0, 14.5, 1600, 2, 0),
    (15.0, 16.5, 1900, 2, 0),
    (17.0, 18.5, 2200, 2, 0),
    (19.0, 20.5, 2500, 2, 0),
    (21.0, 22.5, 3000, 3, 0),
    (23.0, 24.5, 3500, 3, 0),
    (25.0, 25.5, 4000, 3, 0),
    (26.0, 26.5, 4000, 4, 0),
    (27.0, 28.5, 4500, 4, 0),
    (29.0, 30.5, 5000, 4, 0),
    (31.0, 32.5, 6000, 6, 0),
    (33.0, 34.5, 7000, 8, 0),
    (35.0, 36.5, 8000, 10, 0),
    (37.0, 38.5, 9000, 12, 0),
    (39.0, 39.5, 10000, 15, 0),
    (40.0, 40.5, 10000, 0, 10),
    (41.0, 41.5, 11000, 0, 10),
    (42.0, 42.5, 11000, 0, 12),
    (43.0, 43.5, 12000, 0, 12),
    (44.0, 44.5, 12000, 0, 15),
    (45.0, 45.5, 13000, 0, 15),
    (46.0, 46.5, 13000, 0, 17),
    (47.0, 47.5, 14000, 0, 17),
    (48.0, 48.5, 14000, 0, 20),
    (49.0, 49.5, 15000, 0, 20),
)


def _ceil_ratio(value: int, numerator: int, denominator: int) -> int:
    scaled = value * numerator
    return (scaled + denominator - 1) // denominator


def _validate_form(form: PowerUpForm | str) -> PowerUpForm:
    if isinstance(form, PowerUpForm):
        return form
    try:
        return PowerUpForm(form)
    except (TypeError, ValueError) as exc:
        allowed = ", ".join(member.value for member in PowerUpForm)
        raise ValueError(f"form must be one of: {allowed}") from exc


def _base_step_cost(level: float) -> tuple[int, int, int]:
    for low, high, stardust, candy, candy_xl in _COST_BANDS:
        if low <= level <= high:
            return stardust, candy, candy_xl
    raise ValueError(f"no normal power-up cost is defined from level {level:g}")


def power_up_step_cost(
    level: Real,
    *,
    form: PowerUpForm | str = PowerUpForm.NORMAL,
    lucky: bool = False,
) -> PowerUpStepCost:
    """Return the cost of one half-level power-up from level to level + 0.5."""
    current = validate_level(level)
    if current >= MAX_POWER_UP_LEVEL:
        raise ValueError("normal power-ups cannot start at or above level 50")
    if not isinstance(lucky, bool):
        raise TypeError("lucky must be a boolean")
    form_value = _validate_form(form)
    if lucky and form_value is PowerUpForm.SHADOW:
        raise ValueError("a Shadow Pokemon cannot also be Lucky")

    stardust, candy, candy_xl = _base_step_cost(current)

    if form_value is PowerUpForm.NORMAL:
        form_num, form_den = 1, 1
    elif form_value is PowerUpForm.SHADOW:
        form_num, form_den = 6, 5
    else:
        form_num, form_den = 9, 10

    dust_num = form_num
    dust_den = form_den * (2 if lucky else 1)

    return PowerUpStepCost(
        level_from=current,
        level_to=current + 0.5,
        stardust=_ceil_ratio(stardust, dust_num, dust_den),
        candy=_ceil_ratio(candy, form_num, form_den),
        candy_xl=_ceil_ratio(candy_xl, form_num, form_den),
        form=form_value,
        lucky=lucky,
    )


def calculate_power_up_cost(
    start_level: Real,
    target_level: Real,
    *,
    form: PowerUpForm | str = PowerUpForm.NORMAL,
    lucky: bool = False,
) -> PowerUpCost:
    """Calculate total generic resources for repeated half-level power-ups.

    Species-specific exceptions are intentionally outside this deterministic
    generic schedule. The current known exception, Eternatus, should be handled
    by a future species-data layer or an explicit alternate schedule.
    """
    start = validate_level(start_level)
    target = validate_level(target_level)
    if target < start:
        raise ValueError("target_level must be greater than or equal to start_level")
    if target > MAX_POWER_UP_LEVEL:
        raise ValueError("normal power-ups cannot raise a Pokemon above level 50")
    if not isinstance(lucky, bool):
        raise TypeError("lucky must be a boolean")
    form_value = _validate_form(form)
    if lucky and form_value is PowerUpForm.SHADOW:
        raise ValueError("a Shadow Pokemon cannot also be Lucky")

    if start == target:
        return PowerUpCost(
            start_level=start,
            target_level=target,
            power_ups=0,
            stardust=0,
            candy=0,
            candy_xl=0,
            form=form_value,
            lucky=lucky,
        )

    levels = iter_levels(start, target)
    step_levels = levels[:-1]
    steps = [
        power_up_step_cost(level, form=form_value, lucky=lucky)
        for level in step_levels
    ]
    return PowerUpCost(
        start_level=start,
        target_level=target,
        power_ups=len(steps),
        stardust=sum(step.stardust for step in steps),
        candy=sum(step.candy for step in steps),
        candy_xl=sum(step.candy_xl for step in steps),
        form=form_value,
        lucky=lucky,
    )
