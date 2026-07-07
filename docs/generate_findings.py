#!/usr/bin/env python3
"""Generate the 20 agent finding markdown files from collected evidence.

Re-run after regenerating docs/evidence/. Owns only docs/agents/*.md.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path("/workspace")
AGENTS = ROOT / "docs" / "agents"
EV = ROOT / "docs" / "evidence"
AGENTS.mkdir(parents=True, exist_ok=True)


def ev(name: str) -> str:
    p = EV / name
    if not p.exists():
        return f"(missing evidence file: {name})"
    return p.read_text(encoding="utf-8", errors="replace")


def write(name: str, body: str) -> None:
    (AGENTS / name).write_text(body.strip() + "\n", encoding="utf-8")
    print("wrote", name)


def finding(
    title: str,
    scope: str,
    method: str,
    evidence: list[str],
    findings: str,
    verdict: str,
    notes: str = "",
) -> str:
    ev_block = "\n".join(f"- `{e}`" for e in evidence)
    note = f"\n\n{notes}" if notes else ""
    return f"""# {title}

## Scope

{scope}

## Method

{method}

## Evidence

{ev_block}

## Findings

{findings}{note}

## Verdict

`{verdict}`
"""


def main() -> None:
    loc = ev("loc_by_package.tsv")
    packaging = ev("packaging.txt")
    env = ev("env_probe.txt")
    cli_err = ev("01_cli_import_error.txt")
    ann = ev("01_annotations_future.txt")

    write(
        "01-overview-packaging.md",
        finding(
            "Agent 01: Project overview and packaging",
            "Map packaging, installability, Python version gate, and whether the package imports on this host.",
            "Read pyproject.toml and README head. Probe import with python3 3.12 after installing declared core deps. Count packages and LOC via collect_evidence.py.",
            [
                "docs/evidence/packaging.txt",
                "docs/evidence/loc_by_package.tsv",
                "docs/evidence/readme_head.txt",
                "docs/evidence/env_probe.txt",
                "docs/evidence/01_cli_import_error.txt",
                "docs/evidence/01_annotations_future.txt",
                "pyproject.toml",
            ],
            f"""
The project is TheAuditor, a database-first SAST and code-intelligence CLI packaged as `theauditor` version `{packaging.strip().splitlines()[0]}`.

Declared `requires-python` is `>=3.14`. This cloud host runs Python 3.12.3. That alone blocks a supported install story here.

Core deps in pyproject are only click, rich, and loguru. Runtime parsers and ML live under optional `runtime`. That split matches the sandbox `aud setup-ai` story in project docs.

`theauditor` on disk is about 174k lines of Python across 20+ packages. Largest surfaces by LOC: rules (~56k), indexer (~32k), commands (~22k), ast_extractors (~19k).

Import of `theauditor.cli` fails on 3.12 after installing click/rich/loguru with:

```
NameError: name 'RichRenderer' is not defined
```

in `theauditor/pipeline/renderer.py` because `DynamicTable.__init__` annotates `RichRenderer` before the class body exists, and the file lacks `from __future__ import annotations`. Only 10 of 412 Python files use that future import ({ann.strip()}). On 3.14 this may be softened by deferred evaluation; on 3.12 it hard-fails at class body execution time.

README opens with a close-source pivot notice dated 2026-01-23 and says the open tree "is bit broken in some places." Packaging and the import failure are consistent with that claim for this environment.

LOC snapshot:

```
{loc.strip()}
```
""".strip(),
            "VERIFIED",
            "Consumer impact: newcomers cannot `import theauditor.cli` on Python 3.12. Maintainer impact: the 3.14 floor plus missing future annotations makes poly-version support accidental.",
        ),
    )

    write(
        "02-cli-commands.md",
        finding(
            "Agent 02: CLI surface and commands",
            "Inventory Click command modules, registration in cli.py, and whether help is runnable.",
            "List theauditor/commands/*.py. Parse cli.py imports and add_command targets. Attempt import of cli after core deps install.",
            [
                "docs/evidence/cli_command_modules.txt",
                "docs/evidence/02_cli_registration.txt",
                "docs/evidence/01_cli_import_error.txt",
                "theauditor/cli.py",
                "theauditor/commands/",
            ],
            """
Command package has 37 modules under `theauditor/commands/` (excluding `__init__`), spanning full, query, taint, graph, planning, refactor, terraform, cdk, lint, fce, session, ml (`learn`/`suggest`), and others.

`cli.py` imports those command callables and registers them on the Click group. Registered names observed in evidence include full, query, taint_analyze, graph, planning, refactor_command, terraform, setup_ai, workset, boundaries, and ML entry points.

`aud` is not on PATH here and the package is not pip-installed. Direct `from theauditor.cli import main` fails on the renderer forward-reference NameError before any Click help can run.

Therefore CLI surface inventory is VERIFIED from source. End-to-end `aud --help` is NOT VERIFIED on this host.
""".strip(),
            "INCONCLUSIVE",
            "Structure of the CLI is clear from source. Runtime command smoke tests could not run because import aborts first.",
        ),
    )

    tables = ev("03_table_names.txt")
    table_count = [l for l in tables.splitlines() if l.startswith("COUNT=")]
    write(
        "03-indexer.md",
        finding(
            "Agent 03: Indexer and repo_index.db",
            "Assess indexer layout, schema modules, table inventory, and architecture-doc fidelity claims.",
            "List indexer Python files. Parse TableSchema name= across *_schema.py. Read Architecture/01_indexer.md claims. Search CREATE TABLE and repo_index.db references.",
            [
                "docs/evidence/indexer_files.txt",
                "docs/evidence/03_table_names.txt",
                "docs/evidence/03_indexer_schema_hits.txt",
                "docs/evidence/20_indexer_arch_claim.txt",
                "Architecture/01_indexer.md",
                "theauditor/indexer/schemas/",
            ],
            f"""
Indexer is the largest subsystems after rules: 69 Python files, ~32k LOC (`docs/evidence/loc_by_package.tsv`).

Schema layer is explicit: language-specific modules (`python_schema`, `node_schema`, `go_schema`, `rust_schema`, `bash_schema`, `graphql_schema`, `infrastructure_schema`, `security_schema`, `frameworks_schema`, `planning_schema`, `graphs_schema`) plus generated accessors/types.

Parsed `TableSchema(name=...)` definitions: **234 unique table names** ({table_count[0] if table_count else "COUNT=?"}). Architecture/01_indexer.md claims "70+ database tables" and "~2,000 lines across orchestrator, core, and storage." Both claims understate the code as shipped. The fidelity "holy trio" (manifest, receipt, reconciliation) is documented and present in module names.

Default DB path used across commands is `.pf/repo_index.db`. Graph store is separate `.pf/graphs.db` (CLAUDE.md and command help agree).

Runtime indexing (`aud full --index`) was not executed (CLI import broken; no target app fixture required for this review beyond self). Schema and structure are VERIFIED from source.
""".strip(),
            "VERIFIED",
        ),
    )

    write(
        "04-ast-extractors.md",
        finding(
            "Agent 04: AST extractors (polyglot)",
            "Inventory language extractors and check README Java / JS-bundle claims against the tree.",
            "List ast_extractors layout. Inspect JS package.json and dist/extractor.cjs size. Search for java-related paths. Cross-check README pivot claims.",
            [
                "docs/evidence/04_extractor_layout.txt",
                "docs/evidence/04_extractor_names.txt",
                "docs/evidence/04_java_hits.txt",
                "docs/evidence/js_extractor.txt",
                "docs/evidence/readme_head.txt",
                "theauditor/ast_extractors/",
            ],
            """
Extractors exist for Python, JavaScript/TypeScript (TypeScript sources + bundled `dist/extractor.cjs` ~10.3 MB), Go, Rust, Bash, and HCL, plus shared parser helpers.

JS extractor `package.json` builds with esbuild to CJS. Dist artifact is present in-tree, matching hatch force-include in pyproject.

README pivot text claims Java (Maven/Spring/Gradle/Jakarta) is "fully integrated." In this tree, java-named hits are essentially absent (3 path hits, none a Java AST extractor package). Either Java landed only in a closed fork, or the README claim overreaches this snapshot. Treat Java support as **not present here**.

No extractor unit tests were found under a repo `tests/` tree (Agent 17).
""".strip(),
            "VERIFIED",
            "Claim-vs-tree gap on Java is the main fidelity finding for this seam.",
        ),
    )

    write(
        "05-taint.md",
        finding(
            "Agent 05: Taint analysis",
            "Map taint package structure, IFDS / zero-fallback posture, and runnable status.",
            "LOC inventory of theauditor/taint. Read core.py head and grep NO FALLBACKS / except Exception. Note CLI entry taint_analyze.",
            [
                "docs/evidence/taint_files.txt",
                "docs/evidence/05_taint_loc.tsv",
                "docs/evidence/taint_core_head.txt",
                "theauditor/taint/core.py",
                "theauditor/taint/ifds_analyzer.py",
                "theauditor/commands/taint.py",
            ],
            """
Taint is a focused package (~3.9k LOC, 9 modules): core, discovery, flow_resolver, ifds_analyzer, type_resolver, access_path, taint_path, fidelity.

Design voice in source is hard-fail: many `NO FALLBACKS` / `Registry is MANDATORY` raise sites in discovery, flow_resolver, ifds_analyzer, fidelity. That matches the project Zero Fallback law for this subsystem.

`core.py` still contains `except Exception` handlers at least at two call sites (lines ~544 and ~970 per grep). Those need a human judgment pass for whether they swallow and continue (policy violation) or log-and-raise. This review did not prove a silent alternative code path; it only flags the pattern.

End-to-end taint on a fixture was not run (CLI import failure). Structural review of the engine is VERIFIED; behavioral correctness is open.
""".strip(),
            "INCONCLUSIVE",
        ),
    )

    write(
        "06-rules.md",
        finding(
            "Agent 06: Rules engine",
            "Inventory rule categories, METADATA exports, and README '25 categories / 200+ functions' claims.",
            "Count category directories. Count METADATA= exports via rg. Sample orchestrator and category LOC.",
            [
                "docs/evidence/rules_categories.tsv",
                "docs/evidence/rules_metadata_exports.txt",
                "docs/evidence/06_rule_cat_names.txt",
                "docs/evidence/06_metadata_count.txt",
                "theauditor/rules/orchestrator.py",
            ],
            """
Rules dominate the codebase (~56k LOC, 131 Python files). Category directories observed: auth, bash, common, dependency, deployment, frameworks, github_actions, go, graphql, logic, node, orm, performance, python, quality, react, rust, secrets, security, sql, terraform, typescript, vue, xss. That is **24** category dirs (plus supporting base/query modules), near the README "25 rule categories" claim.

`METADATA =` exports: **98** files (rg). That is the lower bound on registered detection units, not yet 200+ functions. Many modules expose multiple analyze helpers beyond METADATA; counting functions would require a deeper static walk. "200+ detection functions" is plausible but **not counted to proof** in this pass.

Orchestrator and per-language/framework analyzers are present. No dedicated rules regression suite under `tests/` (see Agent 17).
""".strip(),
            "VERIFIED",
            "Category inventory VERIFIED. Exact '200+ functions' claim left as unchecked marketing math.",
        ),
    )

    write(
        "07-graph.md",
        finding(
            "Agent 07: Graph subsystem and graphs.db",
            "Map graph package, separation from repo_index.db, and command surface.",
            "LOC inventory of theauditor/graph. Grep graphs.db / repo_index.db usage in commands/graph.py and terraform graph writer.",
            [
                "docs/evidence/07_graph_loc.tsv",
                "docs/evidence/theauditor_packages.txt",
                "theauditor/commands/graph.py",
                "theauditor/indexer/schemas/graphs_schema.py",
            ],
            """
Graph package is substantial (~9.5k LOC, 30 files): strategies, path correlation, fidelity, builders.

Command docs and CLAUDE.md state a hard split: `repo_index.db` for facts, `graphs.db` for precomputed graphs. `commands/graph.py` help text matches that split. Terraform writes a provisioning graph into graphs.db as a custom graph type.

Runtime `aud graph build` was not executed. Dual-database architecture is VERIFIED from source and docs agreement.
""".strip(),
            "VERIFIED",
        ),
    )

    write(
        "08-fce.md",
        finding(
            "Agent 08: FCE (findings correlation engine)",
            "Locate FCE package, command entry, and size relative to pipeline.",
            "List theauditor/fce Python files and LOC. Read package init. Confirm commands/fce.py exists.",
            [
                "docs/evidence/08_fce_loc.tsv",
                "theauditor/fce/",
                "theauditor/commands/fce.py",
            ],
            """
FCE is a small but real package: 6 Python files, ~1.1k LOC. Click command `fce` is registered. Pydantic is listed under optional runtime deps for FCE schema validation in pyproject comments.

No FCE-specific automated tests found. Behavioral correlation quality was not exercised. Structure VERIFIED; output quality INCONCLUSIVE and folded into this verdict as incomplete runtime proof.
""".strip(),
            "INCONCLUSIVE",
        ),
    )

    write(
        "09-pipeline.md",
        finding(
            "Agent 09: Pipeline orchestration",
            "Inspect full pipeline modules and the import-blocking renderer bug.",
            "Read pipeline file list and heads. Reproduce NameError importing RichRenderer via cli. Note run_full_pipeline entrypoints.",
            [
                "docs/evidence/pipeline_files.txt",
                "docs/evidence/09_pipeline_heads.txt",
                "docs/evidence/09_pipeline_functions.txt",
                "docs/evidence/full_command_head.txt",
                "docs/evidence/01_cli_import_error.txt",
                "theauditor/pipeline/renderer.py",
            ],
            """
Pipeline package (~2.5k LOC): pipelines, renderer, events, structures, ui. Key functions: `run_full_pipeline`, `run_taint_sync`, `run_taint_async`, async command helpers.

`commands/full.py` is the user-facing orchestrator wrapping the pipeline.

**Blocker reproduced:** importing the pipeline pulls `renderer.py`, where `DynamicTable` type-annotates `RichRenderer` before that class is defined, without postponed evaluation. Confirmed stack trace saved in `docs/evidence/01_cli_import_error.txt`.

Until that is fixed (future annotations, quoting, or reordering), `aud full` cannot start even when dependencies install. This is a root-cause import defect, not an environment flake.
""".strip(),
            "VERIFIED",
            "Root cause identified and reproduced (principle: fix-root-causes / prove-it-works). Fix is out of scope for this docs-only review.",
        ),
    )

    write(
        "10-linters.md",
        finding(
            "Agent 10: Linters integration",
            "Map linter adapters and DB coupling.",
            "LOC inventory of theauditor/linters. Grep repo_index.db references in mypy/eslint adapters.",
            [
                "docs/evidence/10_linters_loc.tsv",
                "theauditor/linters/",
                "theauditor/commands/lint.py",
            ],
            """
Linters package ~1.9k LOC across ~10 files: base runner, eslint, mypy, config generator. Adapters expect `.pf/repo_index.db` for file sets rather than re-walking the tree.

`subprocess`/`exec` usage appears in linter runners (security Agent 19). Design intent is clear: wrap external tools and persist findings into the Auditor DB world.

No linter integration tests in-repo. Runtime NOT VERIFIED.
""".strip(),
            "INCONCLUSIVE",
        ),
    )

    write(
        "11-context.md",
        finding(
            "Agent 11: Context / AI query layer",
            "Map context package and query/explain/blueprint command roles.",
            "LOC inventory of theauditor/context. Confirm commands context, query, explain, blueprint exist and reference repo_index.db.",
            [
                "docs/evidence/11_context_loc.tsv",
                "theauditor/context/",
                "theauditor/commands/query.py",
                "theauditor/commands/context.py",
                "theauditor/commands/explain.py",
                "theauditor/commands/blueprint.py",
            ],
            """
Context package ~4.5k LOC (7 files). Commands `query`, `context`, `explain`, and `blueprint` form the agent-facing read API over `.pf/repo_index.db`.

This is the product differentiator claimed in README (DB-grounded answers vs file grep). Without a populated DB and a working CLI import, query quality was not measured.

Source presence and intended data dependency are VERIFIED. Behavioral utility INCONCLUSIVE; verdict reflects lack of runtime proof.
""".strip(),
            "INCONCLUSIVE",
        ),
    )

    write(
        "12-planning-refactor.md",
        finding(
            "Agent 12: Planning, refactor, and agent protocols",
            "Review planning/refactor packages and agent markdown protocols.",
            "LOC for planning, refactor, agents. List agent protocol files. Note planning.db vs repo_index.db split from command help.",
            [
                "docs/evidence/12_planning_loc.tsv",
                "docs/evidence/12_refactor_loc.tsv",
                "docs/evidence/12_agents_loc.tsv",
                "theauditor/agents/",
                "theauditor/planning/",
                "theauditor/refactor/",
            ],
            """
`planning/` (~728 LOC) includes manager, verification, shadow_git, examples. Command help describes `.pf/planning/planning.db` as separate and persistent across `aud full`.

`refactor/` (~436 LOC) centers on profiles executed against repo_index.db (hard FileNotFoundError if DB missing; aligns with zero-fallback spirit).

`agents/` is **documentation protocols**, not Python: AGENTS.md plus planning/refactor/security/dataflow markdown and a commands/ dir. Root AGENTS.md and CLAUDE.md point assistants at these. No .py under agents (0 LOC in loc_by_package).

Protocols are present and substantial (hundreds of lines each). Effectiveness on a live ticket was not exercised in this review.
""".strip(),
            "VERIFIED",
        ),
    )

    write(
        "13-framework-detection.md",
        finding(
            "Agent 13: Framework detection",
            "Inspect framework_detector, framework_registry, universal_detector and rule framework categories.",
            "Read heads/stats of the three detector modules. Sample registry string tokens. Note frameworks rule category and detect_frameworks command.",
            [
                "docs/evidence/framework_detector.py_head.txt",
                "docs/evidence/framework_registry.py_head.txt",
                "docs/evidence/universal_detector.py_head.txt",
                "docs/evidence/13_registry_string_tokens.txt",
                "theauditor/commands/detect_frameworks.py",
            ],
            """
Detection is a first-class triad at package root: `framework_detector.py`, `framework_registry.py`, `universal_detector.py`, with frameworks stored into repo_index (detect_frameworks command docs cite frameworks table).

Rules also ship a `frameworks/` category (Django/Flask/FastAPI/React/Vue analyzers per file names elsewhere).

Registry is large and string-rich. Exact supported-framework matrix was not exhaustively enumerated. Detection wiring exists and is VERIFIED at structure level.
""".strip(),
            "VERIFIED",
        ),
    )

    write(
        "14-iac.md",
        finding(
            "Agent 14: Terraform and AWS CDK",
            "Inventory IaC packages and commands.",
            "LOC for terraform/ and aws_cdk/. Confirm Click commands terraform and cdk. Note HCL extractor.",
            [
                "docs/evidence/14_terraform_loc.tsv",
                "docs/evidence/14_aws_cdk_loc.tsv",
                "theauditor/commands/terraform.py",
                "theauditor/commands/cdk.py",
                "theauditor/ast_extractors/hcl_impl.py",
            ],
            """
Terraform package ~675 LOC (3 files) including graph construction into graphs.db. AWS CDK package ~230 LOC (2 files). HCL extractor sits under ast_extractors. Commands `terraform` and `cdk` are registered.

Compared to indexer/rules, IaC is a thin vertical. Capability claims in marketing docs overstate depth relative to LOC, but the seams are real and wired.
""".strip(),
            "VERIFIED",
        ),
    )

    write(
        "15-machinel.md",
        finding(
            "Agent 15: MachineL / ML features",
            "Map MachineL package and ml Click commands.",
            "LOC inventory. Confirm learn / learn_feedback / suggest registration from cli imports. Note numpy/sklearn optional runtime deps.",
            [
                "docs/evidence/15_machinel_loc.tsv",
                "docs/evidence/02_cli_registration.txt",
                "pyproject.toml",
                "theauditor/MachineL/",
                "theauditor/commands/ml.py",
            ],
            """
MachineL ~3.8k LOC (7 files). CLI exposes `learn`, `learn_feedback`, and `suggest` via commands/ml.py.

ML stack is optional (`numpy`, `scikit-learn`, `joblib` under runtime extras). Without those deps and a working CLI, learning loops were not run.

Structural presence VERIFIED; model quality and persistence format not verified at runtime.
""".strip(),
            "INCONCLUSIVE",
        ),
    )

    fb_counts = ev("fallback_heuristic_counts.tsv")
    write(
        "16-zero-fallback.md",
        finding(
            "Agent 16: Zero-fallback policy audit",
            "Heuristic scan of theauditor/ for patterns banned or discouraged by CLAUDE.md Zero Fallback law.",
            "Run regex inventory via collect_evidence fallback_scan: except Exception, bare except, fallback word, hasattr, getattr-default, try/except JSON-ish, table-existence checks.",
            [
                "docs/evidence/fallback_heuristic_counts.tsv",
                "docs/evidence/fallback_heuristic_samples.txt",
                "CLAUDE.md",
                "theauditor/taint/",
            ],
            f"""
CLAUDE.md bans DB query fallbacks, try/except alternate logic paths, and table-existence prechecks. Taint code loudly asserts NO FALLBACKS.

Heuristic counts across `theauditor/`:

```
{fb_counts.strip()}
```

Interpretation:
- `except Exception` (36) and try/except-json-ish (26) are smoke signals, not automatic violations. Each needs semantic review.
- `fallback` word hits (92) are often comments documenting the ban, especially in taint.
- `hasattr` (172) and `getattr` with defaults (51) are common Python and not the specific antipatterns called out, but they can hide missing contracts.
- dict-get-fallbackish (266) is a noisy heuristic.

**Conclusion:** Policy is culturally strong in taint/fidelity modules. Repo-wide enforcement is incomplete; automated bans are not encoded as a lint (see encode-lessons principle). No proof of a multi-query DB fallback in this pass, and no proof of cleanliness either.
""".strip(),
            "INCONCLUSIVE",
        ),
    )

    write(
        "17-tests.md",
        finding(
            "Agent 17: Test coverage and quality",
            "Locate automated tests and assess CI linkage.",
            "Search for tests/, test_*.py, *_test.py. Read pyproject pytest config. Compare to CI workflows.",
            [
                "docs/evidence/tests_inventory.txt",
                "docs/evidence/17_tests_note.txt",
                "docs/evidence/ci_workflows.txt",
                "pyproject.toml",
            ],
            """
**Finding:** `tests/` does not exist. `test_file_count=0` for `test_*.py` / `*_test.py` outside excluded vendor trees.

pyproject still configures pytest (`testpaths = ["tests"]`, pytest/pytest-cov/xdist in optional `dev`). That is scaffolding for tests that are not in this snapshot.

JS extractor package.json defines `npm test` (tsx), but no evidence those tests were run here.

Without a test tree, behavior regression protection for a 174k-LOC analyzer is effectively absent in-repo. This is one of the highest-severity process findings of the review.
""".strip(),
            "VERIFIED",
            "Verified absence is still a VERIFIED finding: the predicate 'tests exist and pass' fails with evidence.",
        ),
    )

    write(
        "18-ci.md",
        finding(
            "Agent 18: CI / GitHub workflows",
            "Inventory GitHub Actions and what gates PRs.",
            "Read .github/workflows/*.yml fully into evidence. Check for test/lint jobs.",
            [
                "docs/evidence/ci_workflows.txt",
                "docs/evidence/18_ci_full.txt",
                ".github/workflows/publish.yml",
            ],
            """
Only workflow present: `publish.yml`. It triggers on version tags, sets up Python 3.14, builds the JS extractor, runs `python -m build`, and publishes to PyPI via OIDC trusted publishing.

There is **no** pull_request workflow for pytest, ruff, mypy, or import smoke. Combined with Agent 17, quality gates on contributions are social/manual only.

Publish pipeline aligning on 3.14 matches pyproject. It does not catch the 3.12 annotation import footgun for contributors on older interpreters.
""".strip(),
            "VERIFIED",
        ),
    )

    write(
        "19-security.md",
        finding(
            "Agent 19: Security posture (defensive review of the tool itself)",
            "Static heuristic for dangerous APIs in theauditor product code, excluding detection-string false positives where obvious.",
            "Regex inventory for subprocess, os.system, eval, exec, pickle.loads, yaml.load, shell=True, mktemp. Separate rules/ hits (often pattern literals) from non-rules runtime calls.",
            [
                "docs/evidence/security_pattern_counts.tsv",
                "docs/evidence/security_pattern_samples.txt",
                "docs/evidence/19_subprocess_non_rules.txt",
            ],
            """
Many `eval`/`exec`/`shell=True`/`pickle` hits live under `theauditor/rules/**` as **detection literals** (the tool hunting those patterns). Those are not automatic self-XSS.

Non-rules `subprocess.*` usage: **33** call sites (venv_install, linters, pipeline, session). That is expected for a meta-tool that shells out to npm, linters, and git. Risk depends on argument construction and `shell=True` (product code hits for shell=True in this scan were mostly rules literals).

`os.system` appears in commands/taint.py and manual_lib01 (needs case-by-case review; not expanded to exploit narrative per policy).

No adversarial pentest was performed. Posture for a local-devtools SAST is broadly "shells out a lot," which is architectural. Highest process risk remains untested publish path, not a specific RCE demo.

Defensive inventory VERIFIED; residual risk judgment INCONCLUSIVE without deeper call-graph review of each subprocess site.
""".strip(),
            "INCONCLUSIVE",
        ),
    )

    write(
        "20-docs-architecture.md",
        finding(
            "Agent 20: Docs and Architecture fidelity",
            "Compare Architecture/ + README claims against measured tree; scan openspec status.",
            "List Architecture/*.md sizes. Diff claimed stats vs LOC/table counts. List openspec changes (active vs archive). Note README pivot banner.",
            [
                "docs/evidence/architecture_files.txt",
                "docs/evidence/20_arch_sizes.tsv",
                "docs/evidence/20_architecture_root_head.txt",
                "docs/evidence/20_openspec_changes.txt",
                "docs/evidence/readme_head.txt",
                "docs/evidence/openspec.txt",
                "Architecture/01_indexer.md",
            ],
            """
Architecture folder has 12 topical docs (indexer, AST, graph, taint, FCE, rules, linters, MachineL, pipeline, context, session, commands) plus root Architecture.md. These are detailed and generally match module boundaries.

Fidelity gaps found:
1. Indexer doc "~2,000 lines" vs ~32k LOC in `theauditor/indexer`.
2. "70+ tables" vs **234** TableSchema names parsed.
3. README Java integration claim vs no Java extractor in tree.
4. README "25 categories / 200+ functions" vs 24 category dirs and 98 METADATA exports (functions not fully counted).
5. README pivot banner states the open tree will not get updates and is partly broken. That matches import breakage and missing tests.

OpenSpec has a large `changes/archive/` history and at least one active change (`add-svelte-extraction`). Spec process exists; not re-validated end to end.
""".strip(),
            "VERIFIED",
            "Docs are rich but several quantitative claims are stale relative to the tree.",
        ),
    )


if __name__ == "__main__":
    main()
