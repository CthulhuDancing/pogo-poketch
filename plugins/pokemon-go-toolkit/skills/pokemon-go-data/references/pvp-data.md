# PvP data

Use this profile for Great League, Ultra League, Master League, cups, current PvP rankings, PvP movesets, and battle-simulation context.

## Preferred routing

1. Use PvPoke for current rankings, recommended movesets, formats, and modeled PvP performance.
2. Use Pokemon GO API or Game Master-derived data for species identity, base stats, move availability, and underlying mechanics needed by deterministic calculations.
3. Use `pokemon-go-calculations` for exact IV rank, CP-cap endpoint, effective stats, stat product, and power-up cost once the required numeric inputs are known.

## Keep modeled and deterministic facts distinct

PvPoke rank, usage context, matchup performance, and recommended movesets are modeled or meta-specific outputs. Treat them separately from exact arithmetic such as CP, level, IV rank, or stat product.

## Freshness

PvP rankings and preferred movesets can change after move rebalances, seasonal rules, and format changes. Fetch current data when the task asks whether a Pokemon is presently good, meta-relevant, or preferred in a specific league or cup.

## Handoff

A useful PvP handoff may include:

- exact species/form;
- current league or format;
- current PvPoke rank or approximate standing when requested;
- recommended fast/charged moves;
- base stats for calculation;
- any format-specific caveat;
- source freshness.

Then invoke `pokemon-go-calculations` for specimen-specific numeric conclusions.
