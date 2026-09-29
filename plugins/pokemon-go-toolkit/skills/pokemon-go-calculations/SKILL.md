---
name: pokemon-go-calculations
description: Perform deterministic Pokemon GO calculations and numeric analysis using bundled scripts. Use for CP, effective stats, league or CP-cap endpoints, PvP IV ranking, stat product, power-up Stardust/Candy/XL costs, species-relative Pokestop Showcase scores, and numeric comparisons. Also use proactively when calculation, enumeration, bounds, or representative scenarios would materially improve another Pokemon GO answer, including when the user's numeric information is incomplete.
---

# Pokemon GO calculations

Use the bundled deterministic calculators as the numeric truth layer. Interpret the user's natural-language input yourself, then pass explicit numeric values to the scripts.

## Core behavior

- Use calculations whenever they materially strengthen a Pokemon GO answer, even when the user did not explicitly ask for arithmetic.
- Treat natural-language interpretation and deterministic calculation as separate steps.
- Do not require complete information when useful conclusions can be produced from the information available.
- Prefer, in order:
  1. exact calculation when inputs are sufficient;
  2. exhaustive enumeration when the unknown search space is reasonably small;
  3. bounds or extrema when the question concerns possibility or limits;
  4. representative scenarios when exhaustive enumeration is disproportionate.
- Do not substitute an arbitrary low/average/high sample when exhaustive enumeration or exact bounds are cheap.
- Clearly distinguish supplied or externally retrieved inputs from calculated outputs.
- Never invent a missing base stat, level, IV, or mechanics value. Use `pokemon-go-data` to retrieve missing factual inputs when appropriate, or state the assumption used for a scenario.
- Keep gameplay judgments separate from arithmetic. This skill can establish ranks, endpoints, costs, ranges, counts, and stat differences; another reasoning layer may decide whether a Pokemon is worth building or meta-relevant.

## Run calculations

Use `scripts/calculate.py`. It emits JSON to stdout and nonzero exit status on invalid inputs.

Available operations:

- `cp`: displayed CP at one level.
- `stats`: effective Attack, Defense, Stamina, HP, and stat product at one level.
- `league`: highest supported half-level at or below an arbitrary CP cap.
- `iv-rank`: rank one exact IV spread under a CP cap.
- `iv-search`: exhaustively enumerate a bounded IV search space and return summary extrema plus optional top results.
- `powerup-cost`: Stardust, Candy, and Candy XL from one level to another.
- `showcase-score`: species-relative "Biggest" Showcase score from specimen measurements, species/form means, XXL height class, IV sum, and explicit XXL status. Use displayed mode for normal in-game rounded measurements and exact mode only for unrounded values.

Use integer base stats and IVs. Levels must be supported half-levels. CP caps are arbitrary positive integers.

### Examples

```bash
python scripts/calculate.py league \
  --base-attack 112 --base-defense 152 --base-stamina 225 \
  --iv-attack 0 --iv-defense 15 --iv-stamina 15 \
  --cap 1500
```

```bash
python scripts/calculate.py iv-rank \
  --base-attack 112 --base-defense 152 --base-stamina 225 \
  --iv-attack 0 --iv-defense 15 --iv-stamina 15 \
  --cap 1500
```

```bash
python scripts/calculate.py iv-search \
  --base-attack 112 --base-defense 152 --base-stamina 225 \
  --cap 1500 \
  --attack-min 0 --attack-max 5 \
  --defense-min 10 --defense-max 15 \
  --stamina-min 10 --stamina-max 15 \
  --top 10
```

```bash
python scripts/calculate.py powerup-cost \
  --start-level 20 --target-level 45.5 --form normal
```

```bash
python scripts/calculate.py showcase-score \
  --height 1.87 --weight 30.00 \
  --mean-height 1.10 --mean-weight 19.00 \
  --xxl-class 1.75 --iv-sum 30 --xxl-status yes \
  --measurement-mode displayed
```

`displayed` mode returns a minimum, central estimate, and maximum based on the displayed measurement resolution. The default assumes height and weight were rounded to 0.01 units. Use `--measurement-mode exact` only when unrounded measurements are actually known. Do not infer XXL status from rounded height; pass the specimen's observed in-game classification.

## Incomplete inputs

When some values are unknown, use the smallest deterministic search that answers the question.

Examples:

- Unknown IV spread: enumerate the relevant IV range instead of guessing a typical spread.
- Known Attack IV but unknown Defense/Stamina: constrain the IV search to that Attack value and enumerate the remaining values.
- Uncertain current level with a small plausible range: evaluate each plausible half-level.
- User asks whether something can fit under a CP cap: calculate extrema or enumerate the constrained cases needed to make that assertion.

If the missing information changes the answer substantially and cannot be bounded usefully, say what remains unknown rather than presenting one scenario as definitive.

## Validation

The bundled unit tests live under `scripts/tests/`. Run them when modifying calculator code:

```bash
PYTHONPATH=scripts python -m unittest discover -s scripts/tests -v
```
