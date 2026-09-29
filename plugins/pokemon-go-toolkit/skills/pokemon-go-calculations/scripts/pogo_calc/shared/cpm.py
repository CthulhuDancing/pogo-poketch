"""Pokemon GO combat power multipliers (CPM) by Pokemon level.

The table is explicit rather than interpolated so boundary CP calculations remain
stable. Standard owned Pokemon can be powered up through level 50; 50.5 and 51
are Best Buddy states. Higher encoded values are included for deterministic
special-context calculations, not as a claim that they are normally powerable.
"""

from __future__ import annotations

import math
from numbers import Real

from .constants import MAX_ENCODED_LEVEL, MIN_LEVEL

CPM_BY_LEVEL: dict[float, float] = {
    1.0: 0.094000000,
    1.5: 0.135137432,
    2.0: 0.166397870,
    2.5: 0.192650919,
    3.0: 0.215732470,
    3.5: 0.236572661,
    4.0: 0.255720050,
    4.5: 0.273530381,
    5.0: 0.290249880,
    5.5: 0.306057377,
    6.0: 0.321087600,
    6.5: 0.335445036,
    7.0: 0.349212680,
    7.5: 0.362457751,
    8.0: 0.375235590,
    8.5: 0.387592406,
    9.0: 0.399567280,
    9.5: 0.411193551,
    10.0: 0.422500010,
    10.5: 0.432926419,
    11.0: 0.443107550,
    11.5: 0.453059958,
    12.0: 0.462798390,
    12.5: 0.472336083,
    13.0: 0.481684950,
    13.5: 0.490855800,
    14.0: 0.499858440,
    14.5: 0.508701765,
    15.0: 0.517393950,
    15.5: 0.525942511,
    16.0: 0.534354330,
    16.5: 0.542635767,
    17.0: 0.550792690,
    17.5: 0.558830576,
    18.0: 0.566754520,
    18.5: 0.574569153,
    19.0: 0.582278910,
    19.5: 0.589887917,
    20.0: 0.597400010,
    20.5: 0.604818814,
    21.0: 0.612157290,
    21.5: 0.619399365,
    22.0: 0.626567130,
    22.5: 0.633644533,
    23.0: 0.640652950,
    23.5: 0.647580967,
    24.0: 0.654435630,
    24.5: 0.661214806,
    25.0: 0.667934000,
    25.5: 0.674577537,
    26.0: 0.681164920,
    26.5: 0.687680648,
    27.0: 0.694143650,
    27.5: 0.700538673,
    28.0: 0.706884210,
    28.5: 0.713164996,
    29.0: 0.719399090,
    29.5: 0.725571552,
    30.0: 0.731700000,
    30.5: 0.734741009,
    31.0: 0.737769480,
    31.5: 0.740785574,
    32.0: 0.743789430,
    32.5: 0.746781211,
    33.0: 0.749761040,
    33.5: 0.752729087,
    34.0: 0.755685510,
    34.5: 0.758630378,
    35.0: 0.761563840,
    35.5: 0.764486065,
    36.0: 0.767397170,
    36.5: 0.770297266,
    37.0: 0.773186500,
    37.5: 0.776064962,
    38.0: 0.778932750,
    38.5: 0.781790055,
    39.0: 0.784636970,
    39.5: 0.787473578,
    40.0: 0.790300010,
    40.5: 0.792803940,
    41.0: 0.795300010,
    41.5: 0.797803920,
    42.0: 0.800300010,
    42.5: 0.802803890,
    43.0: 0.805300010,
    43.5: 0.807803870,
    44.0: 0.810300010,
    44.5: 0.812803840,
    45.0: 0.815300010,
    45.5: 0.817803820,
    46.0: 0.820300010,
    46.5: 0.822803800,
    47.0: 0.825300010,
    47.5: 0.827803780,
    48.0: 0.830300010,
    48.5: 0.832803750,
    49.0: 0.835300010,
    49.5: 0.837803730,
    50.0: 0.840300010,
    50.5: 0.842803710,
    51.0: 0.845300010,
    51.5: 0.847803690,
    52.0: 0.850300000,
    52.5: 0.852803660,
    53.0: 0.855300000,
    53.5: 0.857803640,
    54.0: 0.860300000,
    54.5: 0.862803620,
    55.0: 0.865300000,
}


def validate_level(level: Real) -> float:
    """Validate and canonicalize a half-level Pokemon level."""
    if isinstance(level, bool) or not isinstance(level, Real):
        raise TypeError("level must be a real number")
    value = float(level)
    if not math.isfinite(value):
        raise ValueError("level must be finite")
    doubled = value * 2.0
    if not math.isclose(doubled, round(doubled), abs_tol=1e-9):
        raise ValueError("level must use 0.5 increments")
    canonical = round(doubled) / 2.0
    if canonical < MIN_LEVEL or canonical > MAX_ENCODED_LEVEL:
        raise ValueError(
            f"level must be between {MIN_LEVEL:g} and {MAX_ENCODED_LEVEL:g}"
        )
    return canonical


def get_cpm(level: Real) -> float:
    """Return the exact encoded CPM for a supported half level."""
    canonical = validate_level(level)
    return CPM_BY_LEVEL[canonical]


def iter_levels(start: Real, end: Real) -> tuple[float, ...]:
    """Return inclusive half-levels from start through end."""
    start_level = validate_level(start)
    end_level = validate_level(end)
    if end_level < start_level:
        raise ValueError("end level must be greater than or equal to start level")
    start_tick = int(round(start_level * 2))
    end_tick = int(round(end_level * 2))
    return tuple(tick / 2.0 for tick in range(start_tick, end_tick + 1))
