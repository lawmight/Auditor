# Agent 10: Linters integration

## Scope

Package `theauditor/linters/` and CLI `aud lint` (`theauditor/commands/lint.py`). Which external tools wrap. How file sets are chosen. How findings persist. Pipeline Track B wiring. Architecture/07_linters.md fidelity. Live `aud lint` execution is out of scope while CLI import fails on this host.

## Method

Summed package LOC from `docs/evidence/10_linters_loc.tsv`. Read `base.py`, `linters.py`, all six `*Linter` modules, `config_generator.py`, and `commands/lint.py`. Traced `write_findings_batch` into `indexer/database/base_database.py`. Grepped for `lint.json` writers under `theauditor/`. Cross-checked `Architecture/07_linters.md` and pipeline `("lint", ["--workset"])`. Recorded probes as `docs/evidence/10_*.tsv` and `10_*.txt`.

## Evidence

- `/workspace/docs/evidence/10_linters_loc.tsv` (2046 LOC across 12 files)
- `/workspace/docs/evidence/10_tools_inventory.tsv`
- `/workspace/docs/evidence/10_storage_path.txt`
- `/workspace/docs/evidence/10_arch_drift.txt`
- `/workspace/docs/evidence/10_tests_absent.txt`
- `/workspace/theauditor/linters/__init__.py`
- `/workspace/theauditor/linters/base.py`
- `/workspace/theauditor/linters/linters.py`
- `/workspace/theauditor/linters/ruff.py`
- `/workspace/theauditor/linters/mypy.py`
- `/workspace/theauditor/linters/eslint.py`
- `/workspace/theauditor/linters/clippy.py`
- `/workspace/theauditor/linters/golangci.py`
- `/workspace/theauditor/linters/shellcheck.py`
- `/workspace/theauditor/linters/config_generator.py`
- `/workspace/theauditor/commands/lint.py`
- `/workspace/theauditor/indexer/database/base_database.py` (`write_findings_batch`)
- `/workspace/theauditor/pipeline/pipelines.py` (lint Track B)
- `/workspace/Architecture/07_linters.md`

## Findings

Package is about 2046 LOC across twelve files (ten Python modules plus `package.json` and `pyproject_template.toml`). Largest modules are `config_generator.py` (528), `eslint.py` (229), `base.py` (220), and `mypy.py` (211). Orchestrator is thin (`linters.py` 178).

Six tools are real subclasses of `BaseLinter`:

| Tool name | Class | Language extensions |
|-----------|-------|---------------------|
| ruff | RuffLinter | `.py` |
| mypy | MypyLinter | `.py` |
| eslint | EslintLinter | `.js` `.jsx` `.ts` `.tsx` `.mjs` |
| clippy | ClippyLinter | `.rs` |
| golangci-lint | GolangciLinter | `.go` |
| shellcheck | ShellcheckLinter | `.sh` `.bash` |

`LinterOrchestrator` takes root plus `repo_index.db`. It requires Toolbox sandbox from `aud setup-ai`. File list comes from one SQL query on the `files` table (`file_category = 'source'`). Optional workset filters that list. Queued linters run via `asyncio.gather(..., return_exceptions=True)`. Per-tool skip or failure does not abort peers.

Storage path is database-only in this tree. Successful findings convert with `Finding.to_dict()` then `DatabaseManager.write_findings_batch(findings_dicts, "lint")`. Insert target is `findings_consolidated` in `.pf/repo_index.db`. Batch label is `"lint"` while each row keeps the per-tool `Finding.tool` (`ruff`, `eslint`, and so on). Mypy packs `mypy_code` and related fields into `additional_info` for typed columns. There is no `_write_json_output` and no `lint.json` writer under `theauditor/`. `commands/lint.py` returns `output_files: []` and documents the consolidated table only.

Config prep: when JS/TS files exist, orchestrator runs `ConfigGenerator.prepare_configs()` against the index DB before ESLint. Mypy separately uses `ConfigGenerator.generate_python_config` (optional strict audit pass with `suppressed-risk` category). ESLint still batches for command-line length (`MAX_CMD_LENGTH = 8000`, up to four concurrent batches). Ruff, Mypy, GolangCI, and ShellCheck take full lists. Clippy is crate-level.

CLI and docs drift: `lint.py` help text lists black, pylint, bandit, prettier, tsc, go vet, and hadolint. Those adapters are not in `theauditor/linters/`. `--print-plan` only prints ESLint, Ruff, Mypy. Stats hardcode `tools_run: 3`. Architecture/07_linters.md still claims JSON `.pf/raw/lint.json` and `LinterResult.elapsed`. Code uses `duration` and DB writes only. That JSON claim matches archived OpenSpec remove-raw-json work as intentional removal, so Architecture is stale.

Pipeline stages Track B as `("lint", ["--workset"])` with a 600s timeout slot. No in-repo tests reference `LinterOrchestrator` or the six linter classes. End-to-end `aud lint` was not run. Import chain still dies on `RichRenderer` (`evidence/01_cli_import_error.txt`). Structural map of tools and storage stands on static evidence.

## Verdict

`VERIFIED`
