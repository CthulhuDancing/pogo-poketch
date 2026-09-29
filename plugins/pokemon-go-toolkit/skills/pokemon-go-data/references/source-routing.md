# Source routing and provenance

Choose sources according to the fact being requested rather than forcing one source to answer every Pokemon GO question.

## Primary source families

### PokeMiners Game Master
- Repository: https://github.com/PokeMiners/game_masters
- Best for: mechanics-critical Game Master values and fields that downstream projects derive from the Game Master.
- Strength: closest commonly accessible representation of current game configuration.
- Caution: some fields are obfuscated or can change names; interpret field identity carefully.

### Pokemon GO API
- API/docs: https://pokemon-go-api.github.io/pokemon-go-api/
- Repository: https://github.com/pokemon-go-api/pokemon-go-api
- Best for: convenient normalized species, forms, base stats, types, evolutions, moves, and other broadly useful GO facts.
- Strength: easy public JSON lookup built from Game Master-derived sources.
- Caution: use a mechanics-specific source when exact raw Game Master behavior or highly specialized fields matter.

### PvPoke
- Site: https://pvpoke.com/
- Repository: https://github.com/pvpoke/pvpoke
- Best for: current PvP rankings, recommended movesets, formats, simulations, and PvP-specific move data/context.
- Strength: domain-specific PvP modeling and current ranking outputs.
- Caution: do not treat a PvP rank as a general species fact or PvE evaluation.

### pogo_size
- Repository: https://github.com/bmenrigh/pogo_size
- Best for: showcase and size-system fields extracted from Game Master data, including form-specific size parameters and size-class behavior.
- Strength: specialized extraction and validation logic for Pokemon GO size/showcase work.
- Caution: use the exact form and verify that current extracted data corresponds to a current Game Master when freshness matters.

## Conflict handling

When two sources disagree:

1. Confirm that they refer to the same species, form, move, battle mode, and date/version.
2. Prefer the source specialized for the requested domain.
3. For mechanics-critical static values, prefer current Game Master-derived data over downstream summaries.
4. For modeled outputs such as PvP rankings, treat the model source as authoritative for its own ranking output, not for unrelated mechanics.
5. If disagreement remains material to the answer, preserve both values and explain the unresolved difference rather than silently choosing one.

## Freshness

Record retrieval date or source update context for data that changes with seasons, move rebalance updates, rankings, events, raids, Max Battles, or other live rotations. Static species identity and established base stats need less repeated freshness checking unless a form or mechanic recently changed.
