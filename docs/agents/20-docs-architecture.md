# Agent 20: Docs and Architecture fidelity

## Scope

Compare Architecture/ + README claims against measured tree; scan openspec status.

## Method

List Architecture/*.md sizes. Diff claimed stats vs LOC/table counts. List openspec changes (active vs archive). Note README pivot banner.

## Evidence

- `docs/evidence/architecture_files.txt`
- `docs/evidence/20_arch_sizes.tsv`
- `docs/evidence/20_architecture_root_head.txt`
- `docs/evidence/20_openspec_changes.txt`
- `docs/evidence/readme_head.txt`
- `docs/evidence/openspec.txt`
- `Architecture/01_indexer.md`

## Findings

Architecture folder has 12 topical docs (indexer, AST, graph, taint, FCE, rules, linters, MachineL, pipeline, context, session, commands) plus root Architecture.md. These are detailed and generally match module boundaries.

Fidelity gaps found:
1. Indexer doc "~2,000 lines" vs ~32k LOC in `theauditor/indexer`.
2. "70+ tables" vs **234** TableSchema names parsed.
3. README Java integration claim vs no Java extractor in tree.
4. README "25 categories / 200+ functions" vs 24 category dirs and 98 METADATA exports (functions not fully counted).
5. README pivot banner states the open tree will not get updates and is partly broken. That matches import breakage and missing tests.

OpenSpec has a large `changes/archive/` history and at least one active change (`add-svelte-extraction`). Spec process exists; not re-validated end to end.

Docs are rich but several quantitative claims are stale relative to the tree.

## Verdict

`VERIFIED`
