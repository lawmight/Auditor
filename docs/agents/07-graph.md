# Agent 07: Graph subsystem and graphs.db

## Scope

Graph package under `theauditor/graph/` and the `graphs.db` store. How `aud graph build` relates to `repo_index.db`. Command surface in `theauditor/commands/graph.py`. Pipeline wiring of graph phases. Terraform custom graph writes. Runtime `aud graph build` execution is out of scope when the CLI cannot import on this host.

## Method

Summed package LOC from `docs/evidence/07_graph_loc.tsv`. Read `builder.py`, `db_cache.py`, `store.py`, `dfg_builder.py`, `graphs_schema.py`, and `commands/graph.py`. Grepped dual-db path strings under `theauditor/graph/`. Extracted pipeline `command_order` graph steps and DFG strategy wiring. Cross-checked CLAUDE.md section 5.1 and `Architecture/03_graph.md`. Recorded new probes as `docs/evidence/07_*.txt`.

## Evidence

- `/workspace/docs/evidence/07_graph_loc.tsv` (9513 LOC, 30 files)
- `/workspace/docs/evidence/07_dual_db_paths.txt`
- `/workspace/docs/evidence/07_graph_commands.txt`
- `/workspace/docs/evidence/07_pipeline_graph_steps.txt`
- `/workspace/docs/evidence/07_graphs_schema.txt`
- `/workspace/docs/evidence/07_dfg_strategies.txt`
- `/workspace/docs/evidence/07_terraform_graphs.txt`
- `/workspace/docs/evidence/03_graphs_tables.txt`
- `/workspace/theauditor/graph/builder.py`
- `/workspace/theauditor/graph/db_cache.py`
- `/workspace/theauditor/graph/store.py`
- `/workspace/theauditor/graph/dfg_builder.py`
- `/workspace/theauditor/graph/cfg_builder.py`
- `/workspace/theauditor/indexer/schemas/graphs_schema.py`
- `/workspace/theauditor/commands/graph.py`
- `/workspace/theauditor/pipeline/pipelines.py`
- `/workspace/theauditor/terraform/graph.py`
- `/workspace/Architecture/03_graph.md`
- `/workspace/CLAUDE.md` (section 5.1 Two Databases)

## Findings

Package size is about 9513 LOC across 30 files. Largest modules are `dfg_builder.py` (1202), `builder.py` (1128), `visualizer.py` (757), GraphQL builder (593), and interceptor strategy (497). Public exports are `XGraphBuilder`, `XGraphAnalyzer`, `XGraphStore`, and `GraphVisualizer`.

Dual-database split is hard in code. `XGraphBuilder` and `GraphDatabaseCache` read `.pf/repo_index.db` only (files, refs, import_styles, symbols). Missing index raises `FileNotFoundError` with `Run 'aud full'`. `XGraphStore` defaults to `.pf/graphs.db` and applies `GRAPH_TABLES` (`nodes`, `edges`, `analysis_results`) from `graphs_schema.py`, which states used by graphs.db ONLY.

Build flow: CLI `aud graph build` loads the file list from repo_index, builds import then call graphs via `XGraphBuilder`, and persists with `save_import_graph` / `save_call_graph`. `aud graph build-dfg` uses `DFGBuilder` on repo_index assignment and return tables, then `save_data_flow_graph`. Analyze, hotspots, query, and viz read graphs.db only.

Pipeline `command_order` runs `graph build`, `graph build-dfg`, then later `graph analyze` and four `graph viz` views after index. CLAUDE.md states graphs.db is built FROM repo_index during `aud full` via `aud graph build`. That matches source.

`graphs.db` graph_type values include `import`, `call`, `data_flow`, and `terraform_provisioning`. Terraform reads repo_index and writes a custom graph through `XGraphStore.save_custom_graph`. DFG wires nine strategies (Python/Node ORM, Express, interceptors, bash pipes, Go HTTP/ORM, Rust traits/async). CFG lives in `cfg_builder.py` and is used by `aud cfg`, not the main graph group.

CLI subcommands: `build`, `build-dfg`, `analyze`, `hotspots`, `query`, `viz`. Bidirectional reverse edges exist for IFDS (G3). Cache uses immutable `MappingProxyType` (G7). End-to-end `aud graph build` was not executed here. Structural map and dual-db architecture stand on static evidence.

## Verdict

`VERIFIED`
