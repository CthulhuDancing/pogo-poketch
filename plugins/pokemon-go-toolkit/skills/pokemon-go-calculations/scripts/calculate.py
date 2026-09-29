#!/usr/bin/env python3
"""Stable CLI dispatcher for deterministic Pokemon GO calculations."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, is_dataclass
from enum import Enum
from itertools import product
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from pogo_calc import (  # noqa: E402
    BaseStats,
    IVs,
    PowerUpForm,
    calculate_at_level,
    calculate_effective_stats,
    calculate_power_up_cost,
    calculate_displayed_showcase_range,
    calculate_showcase_score,
    find_league_endpoint,
    rank_iv_spread,
)


def _jsonable(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {key: _jsonable(item) for key, item in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    return value


def _base_stats(args: argparse.Namespace) -> BaseStats:
    return BaseStats(args.base_attack, args.base_defense, args.base_stamina)


def _ivs(args: argparse.Namespace) -> IVs:
    return IVs(args.iv_attack, args.iv_defense, args.iv_stamina)


def _common_stats(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--base-attack", type=int, required=True)
    parser.add_argument("--base-defense", type=int, required=True)
    parser.add_argument("--base-stamina", type=int, required=True)


def _common_ivs(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--iv-attack", type=int, required=True)
    parser.add_argument("--iv-defense", type=int, required=True)
    parser.add_argument("--iv-stamina", type=int, required=True)


def _common_cap(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--cap", type=int, required=True)
    parser.add_argument("--min-level", type=float, default=1.0)
    parser.add_argument("--max-level", type=float, default=50.0)


def _result(operation: str, inputs: dict[str, Any], result: Any) -> dict[str, Any]:
    return {"operation": operation, "inputs": inputs, "result": _jsonable(result)}


def cmd_cp(args: argparse.Namespace) -> dict[str, Any]:
    base = _base_stats(args)
    ivs = _ivs(args)
    calc = calculate_at_level(base, ivs, args.level)
    return _result(
        "cp",
        {"base_stats": asdict(base), "ivs": asdict(ivs), "level": args.level},
        {"level": calc.level, "cpm": calc.cpm, "cp": calc.cp},
    )


def cmd_stats(args: argparse.Namespace) -> dict[str, Any]:
    base = _base_stats(args)
    ivs = _ivs(args)
    stats = calculate_effective_stats(base, ivs, args.level)
    return _result(
        "stats",
        {"base_stats": asdict(base), "ivs": asdict(ivs), "level": args.level},
        stats,
    )


def cmd_league(args: argparse.Namespace) -> dict[str, Any]:
    base = _base_stats(args)
    ivs = _ivs(args)
    endpoint = find_league_endpoint(
        base,
        ivs,
        args.cap,
        min_level=args.min_level,
        max_level=args.max_level,
    )
    return _result(
        "league",
        {
            "base_stats": asdict(base),
            "ivs": asdict(ivs),
            "cap": args.cap,
            "min_level": args.min_level,
            "max_level": args.max_level,
        },
        endpoint,
    )


def cmd_iv_rank(args: argparse.Namespace) -> dict[str, Any]:
    base = _base_stats(args)
    ivs = _ivs(args)
    entry = rank_iv_spread(
        base,
        ivs,
        args.cap,
        min_level=args.min_level,
        max_level=args.max_level,
        iv_floor=args.iv_floor,
        iv_ceiling=args.iv_ceiling,
    )
    return _result(
        "iv-rank",
        {
            "base_stats": asdict(base),
            "ivs": asdict(ivs),
            "cap": args.cap,
            "min_level": args.min_level,
            "max_level": args.max_level,
            "iv_floor": args.iv_floor,
            "iv_ceiling": args.iv_ceiling,
        },
        entry,
    )


def _validate_range(name: str, low: int, high: int) -> None:
    if low < 0 or high > 15 or low > high:
        raise ValueError(f"{name} range must satisfy 0 <= min <= max <= 15")


def cmd_iv_search(args: argparse.Namespace) -> dict[str, Any]:
    _validate_range("attack", args.attack_min, args.attack_max)
    _validate_range("defense", args.defense_min, args.defense_max)
    _validate_range("stamina", args.stamina_min, args.stamina_max)
    if args.top < 0:
        raise ValueError("top must be nonnegative")

    base = _base_stats(args)
    rows: list[dict[str, Any]] = []
    for attack, defense, stamina in product(
        range(args.attack_min, args.attack_max + 1),
        range(args.defense_min, args.defense_max + 1),
        range(args.stamina_min, args.stamina_max + 1),
    ):
        ivs = IVs(attack, defense, stamina)
        endpoint = find_league_endpoint(
            base,
            ivs,
            args.cap,
            min_level=args.min_level,
            max_level=args.max_level,
        )
        if endpoint is None:
            continue
        rows.append({"ivs": asdict(ivs), "endpoint": _jsonable(endpoint)})

    rows.sort(
        key=lambda row: (
            -row["endpoint"]["stats"]["stat_product"],
            -row["endpoint"]["stats"]["defense"],
            -row["endpoint"]["stats"]["hp"],
            -row["endpoint"]["stats"]["attack"],
            -row["endpoint"]["level"],
            row["ivs"]["attack"],
            -row["ivs"]["defense"],
            -row["ivs"]["stamina"],
        )
    )

    for index, row in enumerate(rows, start=1):
        row["search_rank"] = index

    if rows:
        stat_products = [row["endpoint"]["stats"]["stat_product"] for row in rows]
        cps = [row["endpoint"]["cp"] for row in rows]
        levels = [row["endpoint"]["level"] for row in rows]
        summary = {
            "candidate_count": len(rows),
            "stat_product_min": min(stat_products),
            "stat_product_max": max(stat_products),
            "cp_min": min(cps),
            "cp_max": max(cps),
            "level_min": min(levels),
            "level_max": max(levels),
            "best": rows[0],
            "worst": rows[-1],
        }
    else:
        summary = {"candidate_count": 0}

    return {
        "operation": "iv-search",
        "inputs": {
            "base_stats": asdict(base),
            "cap": args.cap,
            "min_level": args.min_level,
            "max_level": args.max_level,
            "attack_range": [args.attack_min, args.attack_max],
            "defense_range": [args.defense_min, args.defense_max],
            "stamina_range": [args.stamina_min, args.stamina_max],
        },
        "result": {
            "summary": summary,
            "top": rows[: args.top] if args.top else [],
        },
    }


def cmd_powerup_cost(args: argparse.Namespace) -> dict[str, Any]:
    result = calculate_power_up_cost(
        args.start_level,
        args.target_level,
        form=PowerUpForm(args.form),
        lucky=args.lucky,
    )
    return _result(
        "powerup-cost",
        {
            "start_level": args.start_level,
            "target_level": args.target_level,
            "form": args.form,
            "lucky": args.lucky,
        },
        result,
    )


def cmd_showcase_score(args: argparse.Namespace) -> dict[str, Any]:
    is_xxl = args.xxl_status == "yes"
    common = {
        "mean_height_m": args.mean_height,
        "mean_weight_kg": args.mean_weight,
        "xxl_height_class": args.xxl_class,
        "iv_sum": args.iv_sum,
        "is_xxl": is_xxl,
    }
    if args.measurement_mode == "exact":
        result = calculate_showcase_score(
            height_m=args.height,
            weight_kg=args.weight,
            **common,
        )
    else:
        result = calculate_displayed_showcase_range(
            displayed_height_m=args.height,
            displayed_weight_kg=args.weight,
            height_resolution_m=args.height_resolution,
            weight_resolution_kg=args.weight_resolution,
            **common,
        )
    return _result(
        "showcase-score",
        {
            "height_m": args.height,
            "weight_kg": args.weight,
            "mean_height_m": args.mean_height,
            "mean_weight_kg": args.mean_weight,
            "xxl_height_class": args.xxl_class,
            "iv_sum": args.iv_sum,
            "is_xxl": is_xxl,
            "measurement_mode": args.measurement_mode,
            "height_resolution_m": args.height_resolution if args.measurement_mode == "displayed" else None,
            "weight_resolution_kg": args.weight_resolution if args.measurement_mode == "displayed" else None,
        },
        result,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    cp = sub.add_parser("cp")
    _common_stats(cp)
    _common_ivs(cp)
    cp.add_argument("--level", type=float, required=True)
    cp.set_defaults(func=cmd_cp)

    stats = sub.add_parser("stats")
    _common_stats(stats)
    _common_ivs(stats)
    stats.add_argument("--level", type=float, required=True)
    stats.set_defaults(func=cmd_stats)

    league = sub.add_parser("league")
    _common_stats(league)
    _common_ivs(league)
    _common_cap(league)
    league.set_defaults(func=cmd_league)

    rank = sub.add_parser("iv-rank")
    _common_stats(rank)
    _common_ivs(rank)
    _common_cap(rank)
    rank.add_argument("--iv-floor", type=int, default=0)
    rank.add_argument("--iv-ceiling", type=int, default=15)
    rank.set_defaults(func=cmd_iv_rank)

    search = sub.add_parser("iv-search")
    _common_stats(search)
    _common_cap(search)
    search.add_argument("--attack-min", type=int, default=0)
    search.add_argument("--attack-max", type=int, default=15)
    search.add_argument("--defense-min", type=int, default=0)
    search.add_argument("--defense-max", type=int, default=15)
    search.add_argument("--stamina-min", type=int, default=0)
    search.add_argument("--stamina-max", type=int, default=15)
    search.add_argument("--top", type=int, default=10)
    search.set_defaults(func=cmd_iv_search)

    cost = sub.add_parser("powerup-cost")
    cost.add_argument("--start-level", type=float, required=True)
    cost.add_argument("--target-level", type=float, required=True)
    cost.add_argument(
        "--form",
        choices=[member.value for member in PowerUpForm],
        default=PowerUpForm.NORMAL.value,
    )
    cost.add_argument("--lucky", action="store_true")
    cost.set_defaults(func=cmd_powerup_cost)

    showcase = sub.add_parser("showcase-score")
    showcase.add_argument("--height", type=float, required=True)
    showcase.add_argument("--weight", type=float, required=True)
    showcase.add_argument("--mean-height", type=float, required=True)
    showcase.add_argument("--mean-weight", type=float, required=True)
    showcase.add_argument("--xxl-class", type=float, required=True)
    showcase.add_argument("--iv-sum", type=int, required=True)
    showcase.add_argument(
        "--measurement-mode",
        choices=["displayed", "exact"],
        default="displayed",
    )
    showcase.add_argument("--height-resolution", type=float, default=0.01)
    showcase.add_argument("--weight-resolution", type=float, default=0.01)
    showcase.add_argument(
        "--xxl-status",
        choices=["yes", "no"],
        required=True,
        help="Use the specimen's in-game XXL classification; do not infer from rounded height.",
    )
    showcase.set_defaults(func=cmd_showcase_score)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = args.func(args)
    except (TypeError, ValueError) as exc:
        print(json.dumps({"error": type(exc).__name__, "message": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(_jsonable(payload), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
