# Agent 01: Project overview and packaging

## Scope

Map packaging, installability, Python version gate, and whether the package imports on this host.

## Method

Read pyproject.toml and README head. Probe import with python3 3.12 after installing declared core deps. Count packages and LOC via collect_evidence.py.

## Evidence

- `docs/evidence/packaging.txt`
- `docs/evidence/loc_by_package.tsv`
- `docs/evidence/readme_head.txt`
- `docs/evidence/env_probe.txt`
- `docs/evidence/01_cli_import_error.txt`
- `docs/evidence/01_annotations_future.txt`
- `pyproject.toml`

## Findings

The project is TheAuditor, a database-first SAST and code-intelligence CLI packaged as `theauditor` version `version=2.0.4rc1`.

Declared `requires-python` is `>=3.14`. This cloud host runs Python 3.12.3. That alone blocks a supported install story here.

Core deps in pyproject are only click, rich, and loguru. Runtime parsers and ML live under optional `runtime`. That split matches the sandbox `aud setup-ai` story in project docs.

`theauditor` on disk is about 174k lines of Python across 20+ packages. Largest surfaces by LOC: rules (~56k), indexer (~32k), commands (~22k), ast_extractors (~19k).

Import of `theauditor.cli` fails on 3.12 after installing click/rich/loguru with:

```
NameError: name 'RichRenderer' is not defined
```

in `theauditor/pipeline/renderer.py` because `DynamicTable.__init__` annotates `RichRenderer` before the class body exists, and the file lacks `from __future__ import annotations`. Only 10 of 412 Python files use that future import (with_future=10
without_future=402). On 3.14 this may be softened by deferred evaluation; on 3.12 it hard-fails at class body execution time.

README opens with a close-source pivot notice dated 2026-01-23 and says the open tree "is bit broken in some places." Packaging and the import failure are consistent with that claim for this environment.

LOC snapshot:

```
package	py_files	lines
(root)	9	4422
MachineL	7	3811
agents	0	0
ast_extractors	44	18733
aws_cdk	2	230
boundaries	5	3728
cache	2	95
commands	38	21734
context	7	4484
fce	6	1136
graph	30	9513
indexer	69	32447
linters	10	1883
package_managers	8	3737
pipeline	7	2508
planning	4	728
refactor	2	436
rules	131	56320
session	8	2146
taint	9	3946
terraform	3	675
utils	11	1550
```

Consumer impact: newcomers cannot `import theauditor.cli` on Python 3.12. Maintainer impact: the 3.14 floor plus missing future annotations makes poly-version support accidental.

## Verdict

`VERIFIED`
