# Agent 08: FCE (findings correlation engine)

## Scope

Locate FCE package, command entry, and size relative to pipeline.

## Method

List theauditor/fce Python files and LOC. Read package init. Confirm commands/fce.py exists.

## Evidence

- `docs/evidence/08_fce_loc.tsv`
- `theauditor/fce/`
- `theauditor/commands/fce.py`

## Findings

FCE is a small but real package: 6 Python files, ~1.1k LOC. Click command `fce` is registered. Pydantic is listed under optional runtime deps for FCE schema validation in pyproject comments.

No FCE-specific automated tests found. Behavioral correlation quality was not exercised. Structure VERIFIED; output quality INCONCLUSIVE and folded into this verdict as incomplete runtime proof.

## Verdict

`INCONCLUSIVE`
