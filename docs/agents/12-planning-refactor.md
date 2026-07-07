# Agent 12: Planning, refactor, and agent protocols

## Scope

Review planning/refactor packages and agent markdown protocols.

## Method

LOC for planning, refactor, agents. List agent protocol files. Note planning.db vs repo_index.db split from command help.

## Evidence

- `docs/evidence/12_planning_loc.tsv`
- `docs/evidence/12_refactor_loc.tsv`
- `docs/evidence/12_agents_loc.tsv`
- `theauditor/agents/`
- `theauditor/planning/`
- `theauditor/refactor/`

## Findings

`planning/` (~728 LOC) includes manager, verification, shadow_git, examples. Command help describes `.pf/planning/planning.db` as separate and persistent across `aud full`.

`refactor/` (~436 LOC) centers on profiles executed against repo_index.db (hard FileNotFoundError if DB missing; aligns with zero-fallback spirit).

`agents/` is **documentation protocols**, not Python: AGENTS.md plus planning/refactor/security/dataflow markdown and a commands/ dir. Root AGENTS.md and CLAUDE.md point assistants at these. No .py under agents (0 LOC in loc_by_package).

Protocols are present and substantial (hundreds of lines each). Effectiveness on a live ticket was not exercised in this review.

## Verdict

`VERIFIED`
