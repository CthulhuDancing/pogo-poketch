# Showcase and size data

Use this profile for Pokemon GO showcases, specimen size evaluation, XXS/XXL reasoning, height/weight distributions, and future deterministic showcase-score calculations.

## Preferred routing

1. Use `pogo_size` for specialized size/showcase extraction and interpretation.
2. Use current Game Master data to verify mechanics-critical or newly changed size fields when needed.
3. Use general species APIs only for supporting identity/base-stat facts; do not assume they expose the complete size system.

## Important fields

Depending on the calculation, retrieve the exact form's:

- recorded mean height;
- recorded mean weight;
- weight standard deviation;
- supported XXS and XXL classes;
- raw extended height boundaries;
- evolution or temporary-form size behavior when relevant;
- the XXL height class used by the scoring model (`1.55`, `1.75`, or `2.00` for supported ordinary forms);
- specimen XXL classification from the game when available;
- IVs or IV sum when the score calculation needs them;
- any changed showcase-specific constants or contest normalization rules required by the current format.

The `pogo_size` extraction tooling is useful because it explicitly derives form-level size parameters from a complete Game Master and validates the extracted data.

## Form discipline

Showcase calculations are sensitive to form-specific size settings. Confirm that the source record matches the specimen's actual form before passing values into a calculator.

If the user provides only displayed height/weight and the exact form is ambiguous, resolve the form before claiming an exact score.

## Handoff

Pass the downstream showcase layer the specimen measurements plus only the species/form constants needed by the scoring calculation. Preserve the source and retrieval date because size-system data can change with Game Master updates.

## Deterministic score handoff

For a standard species-relative "Biggest" calculation, pass `pokemon-go-calculations`:

- displayed or exact specimen height and weight;
- the exact form's mean height and mean weight;
- its supported XXL height class;
- IV sum;
- explicit XXL status.

Use the calculator's `showcase-score` operation. Prefer `displayed` mode for values read from the Pokemon detail screen because the game displays rounded measurements while scoring uses more precise underlying values. This produces a score interval instead of false precision. Use `exact` mode only when the measurements are known to be unrounded.

For multi-species, type, buddy-status, or other event formats, first verify the current contest normalization rules. Do not assume every format uses the single-species scoring model unchanged.
