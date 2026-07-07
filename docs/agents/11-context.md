# Agent 11: Context / AI query layer

## Scope

Context and AI query layer: package `theauditor/context/`, CLI `aud query` / `aud explain` / `aud context`, and how agent protocols obtain SQLite ground truth. Architecture evidence labeled `11_*` is session and agents docs. The context feature itself lives under Architecture `10_context.md` and features `03_context`, `06_explain`, `12_query`. Live end-to-end `aud query` on a populated DB is out of scope while CLI import fails and `.pf/*.db` is absent.

## Method

Inventoried `theauditor/context/` LOC into `docs/evidence/11_context_loc.tsv`. Read `query.py` (`CodeQueryEngine`), `semantic_context.py`, formatters, and `deadcode_graph.py`. Cross-checked commands `query.py`, `explain.py`, `context.py`, `deadcode.py` and CLI registration in `cli.py`. Compared Architecture/10_context.md and features 03/06/12 plus `11_agents.md` and `agents/AGENTS.md` citations. Probed import of `theauditor.cli` and `theauditor.context`. Confirmed DB files and zero-fallback drift. Wrote probes as `docs/evidence/11_*`.

## Evidence

- `/workspace/docs/evidence/11_context_loc.tsv` (4818 LOC across 10 files)
- `/workspace/docs/evidence/11_commands_loc.tsv`
- `/workspace/docs/evidence/11_key_symbols.txt`
- `/workspace/docs/evidence/11_engine_methods.txt`
- `/workspace/docs/evidence/11_db_contract.txt`
- `/workspace/docs/evidence/11_zf_drift.txt`
- `/workspace/docs/evidence/11_arch_map.txt`
- `/workspace/docs/evidence/11_agent_citations.txt`
- `/workspace/docs/evidence/11_session_workflow.txt`
- `/workspace/docs/evidence/11_cli_import.txt`
- `/workspace/docs/evidence/11_context_import.txt`
- `/workspace/docs/evidence/11_direct_import.txt`
- `/workspace/docs/evidence/11_db_presence.txt`
- `/workspace/docs/evidence/11_cli_register.txt`
- `/workspace/docs/evidence/11_depth_drift.txt`
- `/workspace/theauditor/context/query.py`
- `/workspace/theauditor/context/semantic_context.py`
- `/workspace/theauditor/context/__init__.py`
- `/workspace/theauditor/commands/query.py`
- `/workspace/theauditor/commands/explain.py`
- `/workspace/theauditor/commands/context.py`
- `/workspace/theauditor/agents/AGENTS.md`
- `/workspace/Architecture/10_context.md`
- `/workspace/Architecture/features/11_agents.md`
- `/workspace/Architecture/features/12_query.md`
- `/workspace/Architecture/features/06_explain.md`
- `/workspace/Architecture/features/03_context.md`

## Findings

Package is about 4818 LOC across ten files. Core is `query.py` (1890). Next are `deadcode_graph.py` (761), `semantic_context.py` (573), `explain_formatter.py` (474), `formatters.py` (435), `findings_formatter.py` (329). Semantic YAML helpers add about 334 LOC under `semantic_rules/`. Related CLI: `query.py` 786, `explain.py` 482, `context.py` 356, `deadcode.py` 326.

`CodeQueryEngine` is the agent read path. Constructor requires `.pf/repo_index.db` or raises `FileNotFoundError` with `aud full` guidance. Opens `.pf/graphs.db` if present. Else sets `graph_db = None`. Dependency and importer paths call `_require_graph_db()` and raise `RuntimeError` (hard stop, documented zero-fallback). Engine has about 32 methods: symbol resolve and find, recursive CTE callers (depth 1-5), callees, file/symbol context bundles, API/component/findings/pattern/content/category search, variable BFS flow (depth 1-10), taint joins, framework metadata.

How agents get DB truth:

1. Protocol (`AGENTS.md`, `features/11_agents.md`) mandates `aud blueprint` then `aud query` / `aud explain` instead of file reads.
2. CLI registers `query`, `explain`, `context`, `deadcode` on the root Click group.
3. `aud query` and `aud explain` instantiate `CodeQueryEngine` and run SQL against indexed tables (`symbols`, `function_call_args`, `refs`, `findings_consolidated`, and so on).
4. `aud explain` auto-detects file/symbol/component via `detect_target_type` and returns one context bundle.
5. `aud context` applies YAML `SemanticContext` patterns (obsolete/current/transitional) to findings, not to raw AST.
6. Session `WorkflowChecker` scores `query_before_edit` when Bash tool args contain `aud query` or `aud context`.

Zero-fallback drift inside `query.py`: `content_search` and `category_search` use `sqlite_master` / `existing_tables` skips. Comment calls symbol search a "fallback". That violates Architecture Law section 4 table-existence bans. `_require_graph_db` itself is correct hard-fail.

Import blockers on this host: `theauditor.cli` dies on `RichRenderer` forward ref (same as agents 01/09/10). Separately, `theauditor.context` fails because `SemanticContext.load` annotates return type as `SemanticContext` without `from __future__ import annotations`. Commands import via `from theauditor.context import ...` so `aud query` / `aud context` cannot load until that is fixed. No `.pf/repo_index.db` or `graphs.db` in the workspace, so live query was not run.

Doc map: Architecture `11_*` covers session ML and agent orchestration, not the context package. Context system doc is `10_context.md`. Minor drift: Arch 10 says variable-flow depth 5; code allows up to 10 (default 10). Features `06_explain` correctly notes disk snippets only via `CodeSnippetManager` after DB facts.

## Verdict

`VERIFIED`

## 5-line summary

Agents obtain DB truth through `CodeQueryEngine` SQL on `.pf/repo_index.db` (and graphs.db when required), surfaced as `aud query` and `aud explain`.
`aud context` classifies findings with YAML semantic rules. It does not replace the structural query engine.
Agent protocols and session `query_before_edit` encode that path as mandatory evidence before edits.
Structural API, CLI registration, and Architecture claims for that read path match the source tree.
Runtime `aud query` was not executed here (CLI/context import NameErrors, missing index DBs). Query answer quality remains unmeasured.
