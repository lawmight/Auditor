# Agent 05: Taint analysis

## Scope

Map taint package structure, IFDS / zero-fallback posture, and runnable status.

## Method

LOC inventory of theauditor/taint. Read core.py head and grep NO FALLBACKS / except Exception. Note CLI entry taint_analyze.

## Evidence

- `docs/evidence/taint_files.txt`
- `docs/evidence/05_taint_loc.tsv`
- `docs/evidence/taint_core_head.txt`
- `theauditor/taint/core.py`
- `theauditor/taint/ifds_analyzer.py`
- `theauditor/commands/taint.py`

## Findings

Taint is a focused package (~3.9k LOC, 9 modules): core, discovery, flow_resolver, ifds_analyzer, type_resolver, access_path, taint_path, fidelity.

Design voice in source is hard-fail: many `NO FALLBACKS` / `Registry is MANDATORY` raise sites in discovery, flow_resolver, ifds_analyzer, fidelity. That matches the project Zero Fallback law for this subsystem.

`core.py` still contains `except Exception` handlers at least at two call sites (lines ~544 and ~970 per grep). Those need a human judgment pass for whether they swallow and continue (policy violation) or log-and-raise. This review did not prove a silent alternative code path; it only flags the pattern.

End-to-end taint on a fixture was not run (CLI import failure). Structural review of the engine is VERIFIED; behavioral correctness is open.

## Verdict

`INCONCLUSIVE`
