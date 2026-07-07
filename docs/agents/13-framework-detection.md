# Agent 13: Framework detection

## Scope

Inspect framework_detector, framework_registry, universal_detector and rule framework categories.

## Method

Read heads/stats of the three detector modules. Sample registry string tokens. Note frameworks rule category and detect_frameworks command.

## Evidence

- `docs/evidence/framework_detector.py_head.txt`
- `docs/evidence/framework_registry.py_head.txt`
- `docs/evidence/universal_detector.py_head.txt`
- `docs/evidence/13_registry_string_tokens.txt`
- `theauditor/commands/detect_frameworks.py`

## Findings

Detection is a first-class triad at package root: `framework_detector.py`, `framework_registry.py`, `universal_detector.py`, with frameworks stored into repo_index (detect_frameworks command docs cite frameworks table).

Rules also ship a `frameworks/` category (Django/Flask/FastAPI/React/Vue analyzers per file names elsewhere).

Registry is large and string-rich. Exact supported-framework matrix was not exhaustively enumerated. Detection wiring exists and is VERIFIED at structure level.

## Verdict

`VERIFIED`
