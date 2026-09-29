# PvE and combat data

Use this profile for raids, gyms, Team GO Rocket, Dynamax/Gigantamax and Max Battles, attacker performance, tank/support roles, move mechanics, and other PvE combat questions.

## Preferred routing

1. Use current Game Master-derived data for underlying move and species mechanics when exact combat values matter.
2. Use Pokemon GO API for convenient normalized species, form, move, raid, or Max Battle lookup when the needed values are exposed.
3. Use specialist battle-analysis sources only for the modeled output they provide, such as raid difficulty or comparative performance.
4. Use `pokemon-go-calculations` for exact CP/stat/cost arithmetic now, and future deterministic damage/breakpoint calculators once those scripts are added.

## Facts that may matter

Retrieve only what the active PvE question needs, for example:

- attacker and defender base stats;
- typing and type effectiveness;
- fast/charged move availability;
- move power, energy, duration, damage windows, or battle-mode-specific parameters;
- Shadow, Mega, Primal, Dynamax, Gigantamax, or other form/state modifiers;
- raid-boss or Max Battle parameters;
- current move availability or legacy status;
- current raid/Max rotation when the question depends on availability.

## Battle-mode discipline

Pokemon GO reuses move names across systems whose parameters can differ. Confirm that move values correspond to the requested battle mode before using them in a damage model.

Keep current availability separate from intrinsic performance. A Pokemon can be a strong attacker even when it is not currently obtainable.

## Freshness

Move stats, raid rotations, Max Battle availability, and event bonuses can change. Fetch current values when the user asks about present performance, availability, or investment decisions.

## Handoff

Pass downstream PvE reasoning only the facts required for the comparison or calculation, plus source provenance. Avoid loading PvP rankings or showcase data unless the same task explicitly needs them.
