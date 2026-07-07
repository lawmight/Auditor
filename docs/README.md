# TheAuditor project review (2026-07-07)

Docs-only review of `/workspace` (TheAuditor) produced under poteto-mode / figure-it-out.
Twenty investigation seams wrote independent findings under `agents/`.
Evidence under `evidence/` is produced by `collect_evidence.py`.
`verify_findings.py` is the rerunnable done-gate.

## How to re-check

```bash
python3 docs/collect_evidence.py
python3 docs/generate_findings.py   # optional rebuild of agent markdown
python3 docs/verify_findings.py
```

## Executive summary

TheAuditor is a large, database-first SAST and agent-context platform (~174k LOC Python).
Indexing, rules, taint, and graph subsystems are real and deep in source.

This open snapshot is not currently operable on the review host:

1. `requires-python >=3.14` while the host is 3.12.3.
2. `from theauditor.cli import main` fails with `NameError: RichRenderer is not defined` in `theauditor/pipeline/renderer.py` (forward reference without postponed annotations). Reproduced and saved under `evidence/01_cli_import_error.txt`.
3. No `tests/` tree and no PR CI for lint/test. Only a tag-triggered PyPI publish workflow exists.
4. README claims Java integration. No Java extractor package appears in this tree.
5. Architecture quantitative claims (indexer LOC, table counts) are stale versus measured schemas (234 tables).

## Verdict tally

| Verdict | Count | Agents |
|---------|-------|--------|
| VERIFIED | 12 | 01, 03, 04, 06, 07, 09, 12, 13, 14, 17, 18, 20 |
| INCONCLUSIVE | 8 | 02, 05, 08, 10, 11, 15, 16, 19 |
| NOT VERIFIED | 0 | |

INCONCLUSIVE usually means structure was confirmed but runtime behavior could not be exercised because the CLI import aborts first.

## Agent index

| # | File | Focus |
|---|------|-------|
| 01 | [agents/01-overview-packaging.md](agents/01-overview-packaging.md) | Packaging, Python floor, import failure |
| 02 | [agents/02-cli-commands.md](agents/02-cli-commands.md) | Click command inventory |
| 03 | [agents/03-indexer.md](agents/03-indexer.md) | Indexer and schema tables |
| 04 | [agents/04-ast-extractors.md](agents/04-ast-extractors.md) | Polyglot extractors, Java gap |
| 05 | [agents/05-taint.md](agents/05-taint.md) | Taint / IFDS engine |
| 06 | [agents/06-rules.md](agents/06-rules.md) | Rules categories and METADATA |
| 07 | [agents/07-graph.md](agents/07-graph.md) | Graph package and graphs.db |
| 08 | [agents/08-fce.md](agents/08-fce.md) | Findings correlation engine |
| 09 | [agents/09-pipeline.md](agents/09-pipeline.md) | Pipeline and renderer blocker |
| 10 | [agents/10-linters.md](agents/10-linters.md) | External linter adapters |
| 11 | [agents/11-context.md](agents/11-context.md) | Query / context AI layer |
| 12 | [agents/12-planning-refactor.md](agents/12-planning-refactor.md) | Planning, refactor, agent protocols |
| 13 | [agents/13-framework-detection.md](agents/13-framework-detection.md) | Framework detection triad |
| 14 | [agents/14-iac.md](agents/14-iac.md) | Terraform and AWS CDK |
| 15 | [agents/15-machinel.md](agents/15-machinel.md) | MachineL features |
| 16 | [agents/16-zero-fallback.md](agents/16-zero-fallback.md) | Zero-fallback policy heuristic audit |
| 17 | [agents/17-tests.md](agents/17-tests.md) | Missing automated tests |
| 18 | [agents/18-ci.md](agents/18-ci.md) | GitHub Actions (publish only) |
| 19 | [agents/19-security.md](agents/19-security.md) | Defensive self-review of the tool |
| 20 | [agents/20-docs-architecture.md](agents/20-docs-architecture.md) | Docs fidelity vs tree |

## Highest priority follow-ups

1. Fix `pipeline/renderer.py` forward reference (add `from __future__ import annotations`, quote the type, or reorder classes). Prove with `python -c "from theauditor.cli import main"`.
2. Add a minimal smoke CI on PRs (import + ruff) before relying on tag publish.
3. Restore or publish a `tests/` tree. pyproject already points there.
4. Correct README / Architecture quantitative and Java claims to match this tree, or document closed-fork exclusivity.
5. Encode zero-fallback bans as lint or codemod rather than prose-only law.

## Playbook and audit trail

- Designed playbook: [PLAYBOOK.md](PLAYBOOK.md)
- Decision log: [decisions.tsv](decisions.tsv)
- Attention flags: [ATTENTION.md](ATTENTION.md)
- Levers: `collect_evidence.py`, `generate_findings.py`, `verify_findings.py`
