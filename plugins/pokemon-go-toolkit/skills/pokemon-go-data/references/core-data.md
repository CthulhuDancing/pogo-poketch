# Core species and family data

Use this profile for species identity, forms, types, base stats, evolution families, evolution requirements, and general move availability.

## Preferred routing

1. Use Pokemon GO API for convenient normalized lookup when it exposes the needed field.
2. Use current Game Master-derived data when the exact underlying mechanic or form-specific value matters.
3. Cross-check another source only when the field is ambiguous, recently changed, or materially affects a downstream calculation.

## Resolve identity first

Pokemon GO frequently distinguishes forms that share a species name. Preserve the exact form when relevant, including regional forms, costume/event forms when mechanics differ, Shadow/Purified state where relevant, Mega/Primal temporary forms, and Dynamax/Gigantamax distinctions when the task concerns those systems.

Do not merge family members into one record. Fetch the exact family members needed for the task.

## Common facts

Retrieve only what is useful, such as:

- Pokédex number and species name;
- form identifier;
- typing;
- GO base Attack, Defense, and Stamina;
- evolution family relationships;
- evolution costs or requirements;
- available fast and charged moves;
- temporary evolution relationships.

When a downstream calculation only needs base stats, hand off the three numeric base stats and resolved form rather than a complete species payload.
