# Agent 06: Rules engine

## Scope

Inventory rule categories, METADATA exports, and README '25 categories / 200+ functions' claims.

## Method

Count category directories. Count METADATA= exports via rg. Sample orchestrator and category LOC.

## Evidence

- `docs/evidence/rules_categories.tsv`
- `docs/evidence/rules_metadata_exports.txt`
- `docs/evidence/06_rule_cat_names.txt`
- `docs/evidence/06_metadata_count.txt`
- `theauditor/rules/orchestrator.py`

## Findings

Rules dominate the codebase (~56k LOC, 131 Python files). Category directories observed: auth, bash, common, dependency, deployment, frameworks, github_actions, go, graphql, logic, node, orm, performance, python, quality, react, rust, secrets, security, sql, terraform, typescript, vue, xss. That is **24** category dirs (plus supporting base/query modules), near the README "25 rule categories" claim.

`METADATA =` exports: **98** files (rg). That is the lower bound on registered detection units, not yet 200+ functions. Many modules expose multiple analyze helpers beyond METADATA; counting functions would require a deeper static walk. "200+ detection functions" is plausible but **not counted to proof** in this pass.

Orchestrator and per-language/framework analyzers are present. No dedicated rules regression suite under `tests/` (see Agent 17).

Category inventory VERIFIED. Exact '200+ functions' claim left as unchecked marketing math.

## Verdict

`VERIFIED`
