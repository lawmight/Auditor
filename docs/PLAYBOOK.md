# Project Review Playbook (figure-it-out design)

## Phase A Framing

**Definition of done (falsifiable):**
1. `/workspace/docs/` exists with `README.md` indexing all findings.
2. Exactly 20 agent finding files under `/workspace/docs/agents/` with names `01`..`20`.
3. Each finding file has sections: Scope, Method, Evidence, Findings, Verdict (`VERIFIED` | `NOT VERIFIED` | `INCONCLUSIVE`), and Evidence paths that resolve on disk or are marked `runtime-unavailable`.
4. `/workspace/docs/decisions.tsv` has one row per phase gate and per agent completion.
5. `/workspace/docs/verify_findings.py` exits 0 when run against the docs tree.
6. Branch `cursor/project-review-swarm-26fb` pushed with docs committed (no Co-authored-by).

**Scope:** Read-only review of TheAuditor (`theauditor/` ~174k LOC Python, Architecture/, openspec/, CI). Deliverable is documentation under `/docs`. No product code mutation.

**Rigor:** High evidence bar (claims cite paths/commands). Breadth prioritized across 20 seams over deep single-module rewrite analysis. Docs-only is reversible.

**Blockers noted before run:**
- No `Task` spawn tool in this cloud run; swarm executes as parallel owned investigation tracks under one orchestrator (same contract as poteto-agent delegates).
- `python` missing; use `python3`.
- Package requires Python >=3.14; environment may not satisfy install/test fully.
- Repo README states pivot/stagnation; treat "broken in places" as a hypothesis to evidence, not accept on faith.

## Phase B Designed Units (20 seams)

Each agent owns one file. No shared mutable write target.

| ID | Seam | Output |
|----|------|--------|
| 01 | Project overview & packaging | `agents/01-overview-packaging.md` |
| 02 | CLI surface & commands | `agents/02-cli-commands.md` |
| 03 | Indexer & repo_index.db | `agents/03-indexer.md` |
| 04 | AST extractors (polyglot) | `agents/04-ast-extractors.md` |
| 05 | Taint analysis | `agents/05-taint.md` |
| 06 | Rules engine | `agents/06-rules.md` |
| 07 | Graph / graphs.db | `agents/07-graph.md` |
| 08 | FCE (findings correlation) | `agents/08-fce.md` |
| 09 | Pipeline orchestration | `agents/09-pipeline.md` |
| 10 | Linters integration | `agents/10-linters.md` |
| 11 | Context / AI query layer | `agents/11-context.md` |
| 12 | Planning & refactor agents | `agents/12-planning-refactor.md` |
| 13 | Framework detection | `agents/13-framework-detection.md` |
| 14 | Terraform / AWS CDK | `agents/14-iac.md` |
| 15 | MachineL / ML | `agents/15-machinel.md` |
| 16 | Zero-fallback policy audit | `agents/16-zero-fallback.md` |
| 17 | Test coverage & quality | `agents/17-tests.md` |
| 18 | CI / GitHub workflows | `agents/18-ci.md` |
| 19 | Security posture (defensive) | `agents/19-security.md` |
| 20 | Docs / Architecture fidelity | `agents/20-docs-architecture.md` |

## Verification harness

`docs/verify_findings.py` checks count, required sections, and verdict enum.
