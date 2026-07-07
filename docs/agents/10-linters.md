# Agent 10: Linters integration

## Scope

Map linter adapters and DB coupling.

## Method

LOC inventory of theauditor/linters. Grep repo_index.db references in mypy/eslint adapters.

## Evidence

- `docs/evidence/10_linters_loc.tsv`
- `theauditor/linters/`
- `theauditor/commands/lint.py`

## Findings

Linters package ~1.9k LOC across ~10 files: base runner, eslint, mypy, config generator. Adapters expect `.pf/repo_index.db` for file sets rather than re-walking the tree.

`subprocess`/`exec` usage appears in linter runners (security Agent 19). Design intent is clear: wrap external tools and persist findings into the Auditor DB world.

No linter integration tests in-repo. Runtime NOT VERIFIED.

## Verdict

`INCONCLUSIVE`
