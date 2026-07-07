# Agent 08: FCE (Findings / Factual Correlation Engine)

## Scope

Package `theauditor/fce/` and CLI `aud fce`. What four vectors correlate at a file. Which DB tables drive vector detection versus context expansion. Pipeline placement. Runtime `aud fce` execution is out of scope when pydantic or a populated `.pf/repo_index.db` is missing on this host.

## Method

Refreshed package LOC in `docs/evidence/08_fce_loc.tsv`. Read `query.py`, `registry.py`, `schema.py`, `engine.py`, `formatter.py`, `__init__.py`, and `commands/fce.py`. Grepped vector and table references under `theauditor/fce/`. Extracted pipeline `fce` wiring. Compared Architecture/05_fce.md claims to code. Probed for tests named around FCE. Wrote new probes as `docs/evidence/08_*.txt`.

## Evidence

- `/workspace/docs/evidence/08_fce_loc.tsv` (1136 LOC, 6 files)
- `/workspace/docs/evidence/08_query_db_sources.txt`
- `/workspace/docs/evidence/08_vector_query_tables.txt`
- `/workspace/docs/evidence/08_registry_risk_sources.txt`
- `/workspace/docs/evidence/08_graph_db_usage.txt`
- `/workspace/docs/evidence/08_command_surface.txt`
- `/workspace/docs/evidence/08_pipeline_fce.txt`
- `/workspace/docs/evidence/08_tests_hits.txt`
- `/workspace/docs/evidence/08_write_flag_claim.txt`
- `/workspace/theauditor/fce/query.py`
- `/workspace/theauditor/fce/registry.py`
- `/workspace/theauditor/fce/schema.py`
- `/workspace/theauditor/fce/engine.py`
- `/workspace/theauditor/commands/fce.py`
- `/workspace/theauditor/pipeline/pipelines.py`
- `/workspace/Architecture/05_fce.md`

## Findings

Package is six Python modules totaling 1136 LOC. Largest is `query.py` (436). Entry is `run_fce` / `get_fce_json` via Click command `fce` with `--root`, `--format text|json`, `--min-vectors` (1-4, default 2), and `--detailed`.

Four vectors are hard-coded in `schema.Vector`: STATIC, FLOW, PROCESS, STRUCTURAL. Density is `len(vectors_present) / 4`. Multiple tools in one vector still count as one vector. Convergence is file-level: files with at least `min_vectors` present become `ConvergencePoint` objects holding facts plus line span.

DB sources for correlation are almost entirely `repo_index.db`. `FCEQueryEngine` hard-fails with FileNotFoundError if that DB is missing. Vector index uses two queries: `findings_consolidated` (tool `cfg-analysis` -> STRUCTURAL, `churn-analysis` -> PROCESS, other tools except `graph-analysis` -> STATIC) and `taint_flows` (source_file or sink_file -> FLOW). Facts for a file come from the same two tables.

`SemanticTableRegistry` lists seven RISK_SOURCES and about 147 categorized context tables. Context expansion in `get_context_bundle` loads extension-matched language and framework tables, plus only tables present with cached columns. RISK_SOURCES beyond `findings_consolidated` and `taint_flows` (cdk, terraform, graphql cache, python_security, framework_taint_patterns) are registered but never queried for vector detection. Package `__init__` docstring still names `framework_taint_patterns` as a FLOW source. That is docstring drift.

`graphs.db` may be opened if present. No FCE correlation path reads it. Only connect/close appear. Pipeline stages `fce` late (timeout 900s) and can write `.pf/fce.log`. No automated FCE tests under test paths (`08_tests_hits.txt` is empty). Architecture/05_fce.md documents `aud fce --write` to `.pf/raw/fce.json`, but the Click command has no `--write` option. Formatter mentions `--write` in a comment only.

Structural map of what FCE correlates and which DB tables it uses is clear from source. Live correlation quality was not exercised here.

## Verdict

`VERIFIED`
