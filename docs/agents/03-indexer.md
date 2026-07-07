# Agent 03: Indexer and repo_index.db

## Scope

Assess indexer layout, schema modules, table inventory, and architecture-doc fidelity claims.

## Method

List indexer Python files. Parse TableSchema name= across *_schema.py. Read Architecture/01_indexer.md claims. Search CREATE TABLE and repo_index.db references.

## Evidence

- `docs/evidence/indexer_files.txt`
- `docs/evidence/03_table_names.txt`
- `docs/evidence/03_indexer_schema_hits.txt`
- `docs/evidence/20_indexer_arch_claim.txt`
- `Architecture/01_indexer.md`
- `theauditor/indexer/schemas/`

## Findings

Indexer is the largest subsystems after rules: 69 Python files, ~32k LOC (`docs/evidence/loc_by_package.tsv`).

Schema layer is explicit: language-specific modules (`python_schema`, `node_schema`, `go_schema`, `rust_schema`, `bash_schema`, `graphql_schema`, `infrastructure_schema`, `security_schema`, `frameworks_schema`, `planning_schema`, `graphs_schema`) plus generated accessors/types.

Parsed `TableSchema(name=...)` definitions: **234 unique table names** (COUNT=234). Architecture/01_indexer.md claims "70+ database tables" and "~2,000 lines across orchestrator, core, and storage." Both claims understate the code as shipped. The fidelity "holy trio" (manifest, receipt, reconciliation) is documented and present in module names.

Default DB path used across commands is `.pf/repo_index.db`. Graph store is separate `.pf/graphs.db` (CLAUDE.md and command help agree).

Runtime indexing (`aud full --index`) was not executed (CLI import broken; no target app fixture required for this review beyond self). Schema and structure are VERIFIED from source.

## Verdict

`VERIFIED`
