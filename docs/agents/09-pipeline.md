# Agent 09: Pipeline orchestration

## Scope

Inspect full pipeline modules and the import-blocking renderer bug.

## Method

Read pipeline file list and heads. Reproduce NameError importing RichRenderer via cli. Note run_full_pipeline entrypoints.

## Evidence

- `docs/evidence/pipeline_files.txt`
- `docs/evidence/09_pipeline_heads.txt`
- `docs/evidence/09_pipeline_functions.txt`
- `docs/evidence/full_command_head.txt`
- `docs/evidence/01_cli_import_error.txt`
- `theauditor/pipeline/renderer.py`

## Findings

Pipeline package (~2.5k LOC): pipelines, renderer, events, structures, ui. Key functions: `run_full_pipeline`, `run_taint_sync`, `run_taint_async`, async command helpers.

`commands/full.py` is the user-facing orchestrator wrapping the pipeline.

**Blocker reproduced:** importing the pipeline pulls `renderer.py`, where `DynamicTable` type-annotates `RichRenderer` before that class is defined, without postponed evaluation. Confirmed stack trace saved in `docs/evidence/01_cli_import_error.txt`.

Until that is fixed (future annotations, quoting, or reordering), `aud full` cannot start even when dependencies install. This is a root-cause import defect, not an environment flake.

Root cause identified and reproduced (principle: fix-root-causes / prove-it-works). Fix is out of scope for this docs-only review.

## Verdict

`VERIFIED`
