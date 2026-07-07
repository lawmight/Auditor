# Agent 07: Graph subsystem and graphs.db

## Scope

Map graph package, separation from repo_index.db, and command surface.

## Method

LOC inventory of theauditor/graph. Grep graphs.db / repo_index.db usage in commands/graph.py and terraform graph writer.

## Evidence

- `docs/evidence/07_graph_loc.tsv`
- `docs/evidence/theauditor_packages.txt`
- `theauditor/commands/graph.py`
- `theauditor/indexer/schemas/graphs_schema.py`

## Findings

Graph package is substantial (~9.5k LOC, 30 files): strategies, path correlation, fidelity, builders.

Command docs and CLAUDE.md state a hard split: `repo_index.db` for facts, `graphs.db` for precomputed graphs. `commands/graph.py` help text matches that split. Terraform writes a provisioning graph into graphs.db as a custom graph type.

Runtime `aud graph build` was not executed. Dual-database architecture is VERIFIED from source and docs agreement.

## Verdict

`VERIFIED`
