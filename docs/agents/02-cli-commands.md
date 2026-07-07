# Agent 02: CLI surface and commands

## Scope

Inventory Click command modules, registration in cli.py, and whether help is runnable.

## Method

List theauditor/commands/*.py. Parse cli.py imports and add_command targets. Attempt import of cli after core deps install.

## Evidence

- `docs/evidence/cli_command_modules.txt`
- `docs/evidence/02_cli_registration.txt`
- `docs/evidence/01_cli_import_error.txt`
- `theauditor/cli.py`
- `theauditor/commands/`

## Findings

Command package has 37 modules under `theauditor/commands/` (excluding `__init__`), spanning full, query, taint, graph, planning, refactor, terraform, cdk, lint, fce, session, ml (`learn`/`suggest`), and others.

`cli.py` imports those command callables and registers them on the Click group. Registered names observed in evidence include full, query, taint_analyze, graph, planning, refactor_command, terraform, setup_ai, workset, boundaries, and ML entry points.

`aud` is not on PATH here and the package is not pip-installed. Direct `from theauditor.cli import main` fails on the renderer forward-reference NameError before any Click help can run.

Therefore CLI surface inventory is VERIFIED from source. End-to-end `aud --help` is NOT VERIFIED on this host.

Structure of the CLI is clear from source. Runtime command smoke tests could not run because import aborts first.

## Verdict

`INCONCLUSIVE`
