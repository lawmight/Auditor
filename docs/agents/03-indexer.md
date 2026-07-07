# Agent 03: Indexer and repo_index.db

## Scope

Indexer package and `repo_index.db` schema under `theauditor/indexer/`.
Covers schema registry, CREATE TABLE generation, and how indexing writes into the DB.
`graphs.db` tables in `graphs_schema.py` are noted only for boundary clarity.

## Method

1. Inventory `theauditor/indexer/` (69 Python files) and `schemas/*_schema.py`.
2. Count `TableSchema(name=...)` per schema module. Separate `GRAPH_TABLES` from `TABLES`.
3. Trace `create_table_sql` in `schemas/utils.py` and `create_schema` in `database/base_database.py`.
4. Trace write path: `runner.run_repository_index` to orchestrator, extractors, `DataStorer`, `flush_batch`.
5. Refresh evidence under `docs/evidence/03_*.txt`.

## Evidence

- `docs/evidence/03_table_names.txt` (COUNT=231 repo_index tables)
- `docs/evidence/03_graphs_tables.txt` (COUNT=3 graphs.db only)
- `docs/evidence/03_create_tables.txt` (CREATE TABLE generation sites)
- `docs/evidence/03_indexer_schema_hits.txt`
- `theauditor/indexer/schema.py` (`TABLES`, `FLUSH_ORDER`)
- `theauditor/indexer/schemas/utils.py` (`TableSchema.create_table_sql`)
- `theauditor/indexer/database/base_database.py` (`create_schema`, `flush_batch`)
- `theauditor/indexer/runner.py` (default `db_path=".pf/repo_index.db"`)
- `theauditor/indexer/orchestrator.py` (`IndexerOrchestrator.index`)
- `theauditor/indexer/storage/__init__.py` (`DataStorer.store`)
- `theauditor/pipeline/pipelines.py` (in-process call to `run_repository_index`)

### Schema module counts (`TableSchema(`)

| Module | Tables |
|--------|--------|
| `core_schema.py` | 24 |
| `security_schema.py` | 7 |
| `frameworks_schema.py` | 7 |
| `python_schema.py` | 37 |
| `node_schema.py` | 51 |
| `rust_schema.py` | 23 |
| `go_schema.py` | 24 |
| `bash_schema.py` | 10 |
| `infrastructure_schema.py` | 29 |
| `planning_schema.py` | 9 |
| `graphql_schema.py` | 10 |
| **Sum in `TABLES`** | **231** |
| `graphs_schema.py` (not merged into `TABLES`) | 3 |
| **All `*_schema.py`** | **234** |

## Findings

`schema.py` is the repo_index SSOT. It builds `TABLES` by merging eleven dicts (`CORE_TABLES` through `GRAPHQL_TABLES`). `graphs_schema.GRAPH_TABLES` is documented for `graphs.db` only and is not imported into `TABLES`.

`TableSchema.create_table_sql()` emits `CREATE TABLE IF NOT EXISTS`. `BaseDatabaseManager.create_schema()` iterates every entry in `TABLES`, executes that SQL, then creates indexes and two unified views (`function_returns_unified`, `symbols_unified`). The compatibility wrapper is `database.create_database_schema`.

Indexing feed path is linear. `run_repository_index` opens `.pf/repo_index.db`, creates the schema, then constructs `IndexerOrchestrator`. The orchestrator clears tables, walks files, selects extractors, and stores via `DataStorer.store`. Batches flush with `FLUSH_ORDER` (207 INSERT targets). Twenty-four tables exist in `TABLES` but not in `FLUSH_ORDER` (for example CFG, taint, and some Angular or Vue child tables). Those are created and may be filled by other writers or later phases.

Pipeline entry is `theauditor/pipeline/pipelines.py`, which calls `run_repository_index` in-process for the index phase. Default DB path is `.pf/repo_index.db`.

This host could not import a full CLI run (Python gate elsewhere). Schema inventory and write-path structure are verified from source without executing `aud full --index`.

## Verdict

`VERIFIED`
