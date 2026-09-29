---
name: pokemon-go-data
description: Retrieve reliable, task-relevant Pokemon GO facts for species, forms, families, evolutions, moves, base stats, PvP context, PvE/combat mechanics, and showcase/size calculations. Use when another Pokemon GO task needs factual inputs from external sources, when freshness matters, or when source-specific data should be routed by domain. The agent owns network retrieval; this skill directs source choice, extraction, provenance, and handoff rather than requiring one universal schema.
---

# Pokemon GO data

Act as a retrieval and handoff layer between external Pokemon GO data sources and downstream reasoning or calculation skills.

The agent owns network access. Fetch data with available web or connector tools, then extract the smallest reliable set of facts needed by the active task. Do not expect bundled scripts to perform network calls.

## Workflow

1. Identify the task profile before fetching data.
2. Resolve the exact species, form, family member, move, or temporary form that the task concerns.
3. Read the matching profile reference below.
4. Fetch only the sources needed for the requested facts.
5. Preserve source provenance and freshness for facts that may change.
6. Resolve material source conflicts before passing data onward.
7. Hand downstream skills the useful facts directly. Normalize only when a deterministic consumer requires a specific input shape.

## Profiles

- **Core species and family data:** read `references/core-data.md`.
- **Showcase and size data:** read `references/showcase-data.md`.
- **PvP data:** read `references/pvp-data.md`.
- **PvE, raids, Rocket, Max Battles, and combat mechanics:** read `references/combat-data.md`.
- **Source selection and conflict handling:** read `references/source-routing.md` whenever more than one source could reasonably answer the request or source reliability matters.

A task may use more than one profile. Fetch each branch independently when the required facts differ, then merge only the facts needed for the downstream answer.

## Handoff behavior

Prefer a compact factual handoff rather than a universal Pokemon object. Include:

- resolved subject identity, including form when relevant;
- facts needed by the downstream task;
- source or sources used;
- freshness or retrieval date when the fact can change;
- material caveats or unresolved conflicts.

A lightweight object is useful when another skill or script will consume the result:

```json
{
  "profile": "showcase",
  "subject": {"species": "Ninetales", "form": "Alolan"},
  "facts": {},
  "provenance": [],
  "caveats": []
}
```

Treat `facts` as task-specific. Do not force showcase dimensions, PvP rankings, combat move timing, evolution requirements, and unrelated fields into one shared schema.

## Using calculations

When retrieved facts are inputs to deterministic arithmetic, pass the explicit values to `pokemon-go-calculations` rather than reproducing the formula mentally.

Examples:

- base stats + IVs + CP cap -> league endpoint or IV rank;
- current level + target level + form state -> power-up cost;
- future showcase size constants + specimen measurements -> showcase calculation;
- future combat move parameters + attacker/defender stats -> damage or breakpoint calculation.

## Network-runtime rule

Keep network retrieval in the agent layer for compatibility with normal ChatGPT runtimes. Local scripts may parse, validate, transform, or calculate from already-retrieved input when that complexity is justified, but they should not depend on outbound network access.
