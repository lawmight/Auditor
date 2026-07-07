# Agent 11: Context / AI query layer

## Scope

Map context package and query/explain/blueprint command roles.

## Method

LOC inventory of theauditor/context. Confirm commands context, query, explain, blueprint exist and reference repo_index.db.

## Evidence

- `docs/evidence/11_context_loc.tsv`
- `theauditor/context/`
- `theauditor/commands/query.py`
- `theauditor/commands/context.py`
- `theauditor/commands/explain.py`
- `theauditor/commands/blueprint.py`

## Findings

Context package ~4.5k LOC (7 files). Commands `query`, `context`, `explain`, and `blueprint` form the agent-facing read API over `.pf/repo_index.db`.

This is the product differentiator claimed in README (DB-grounded answers vs file grep). Without a populated DB and a working CLI import, query quality was not measured.

Source presence and intended data dependency are VERIFIED. Behavioral utility INCONCLUSIVE; verdict reflects lack of runtime proof.

## Verdict

`INCONCLUSIVE`
