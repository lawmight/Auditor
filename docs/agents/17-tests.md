# Agent 17: Test coverage and quality

## Scope

Locate automated tests and assess CI linkage.

## Method

Search for tests/, test_*.py, *_test.py. Read pyproject pytest config. Compare to CI workflows.

## Evidence

- `docs/evidence/tests_inventory.txt`
- `docs/evidence/17_tests_note.txt`
- `docs/evidence/ci_workflows.txt`
- `pyproject.toml`

## Findings

**Finding:** `tests/` does not exist. `test_file_count=0` for `test_*.py` / `*_test.py` outside excluded vendor trees.

pyproject still configures pytest (`testpaths = ["tests"]`, pytest/pytest-cov/xdist in optional `dev`). That is scaffolding for tests that are not in this snapshot.

JS extractor package.json defines `npm test` (tsx), but no evidence those tests were run here.

Without a test tree, behavior regression protection for a 174k-LOC analyzer is effectively absent in-repo. This is one of the highest-severity process findings of the review.

Verified absence is still a VERIFIED finding: the predicate 'tests exist and pass' fails with evidence.

## Verdict

`VERIFIED`
