---
name: pokemon-go-showcases
description: Answer Pokemon GO Pokestop Showcase, largest, XXL/XXS, trophy-size, showcase score, comparison, evolution-size, and practical keep-or-transfer questions. Use for messy size/showcase prompts where the agent should infer obvious facts, retrieve the right species/form data, and use deterministic calculations when they materially improve reliability or efficiency.
---

# Pokemon GO showcases

Use this skill as the routing layer for Showcase and Pokemon size questions.

Use [`pokemon-go-data`](../pokemon-go-data/SKILL.md) to retrieve current species/form size data and showcase mechanics. Use [`pokemon-go-calculations`](../pokemon-go-calculations/SKILL.md) for deterministic scoring and numeric comparisons.

## Workflow

Determine what the user is actually asking: score, rarity, classification, comparison, evolution, or practical showcase value.

Retrieve only the species/form data needed for that question.

Make safe inferences from supplied measurements when possible, especially XXL status.

Use the calculator when it materially improves reliability or efficiency.

## Using the calculator

For ordinary in-game measurements, use displayed-measurement mode so rounding uncertainty is preserved.

Do not limit the calculator to one run when several cheap calculations would give a better answer.

Examples:

- If IVs are unknown, calculate useful low/high or representative outcomes instead of stopping for more information.
- If comparing several Pokemon, score all supplied specimens on the same basis.
- If the question concerns an evolution family, calculate relevant family members when that comparison is useful.
- If several plausible cases can be checked cheaply, evaluate them rather than choosing one arbitrary example.
- Use calculator output as the numeric truth layer when the calculator already supports the required operation.

For missing inputs, use the calculator to produce a modest range of outputs based on representative assumptions for unknown stats.

## Size and rarity

Use `pokemon-go-data` for size distributions, XXL/XXS boundaries, form differences, and evolution behavior.

If a displayed measurement remains entirely inside a size class after rounding is considered, infer that classification. If it can cross a boundary, keep the result uncertain.

Use calculator support for substantial or repeated numeric work when available. Simple arithmetic may be handled directly when that is faster and equally reliable.

## Answering the user

Keep the final answer focused on the decision or comparison they actually care about.

Lead with the conclusion, then give the score, range, threshold, percentile, or comparison that supports it.

## Boundaries

This skill handles interpretation, routing, safe inference, and presentation.

`pokemon-go-data` handles external facts and source selection.

`pokemon-go-calculations` handles deterministic numeric work.