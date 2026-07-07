# Agent 19: Security posture (defensive review of the tool itself)

## Scope

Static heuristic for dangerous APIs in theauditor product code, excluding detection-string false positives where obvious.

## Method

Regex inventory for subprocess, os.system, eval, exec, pickle.loads, yaml.load, shell=True, mktemp. Separate rules/ hits (often pattern literals) from non-rules runtime calls.

## Evidence

- `docs/evidence/security_pattern_counts.tsv`
- `docs/evidence/security_pattern_samples.txt`
- `docs/evidence/19_subprocess_non_rules.txt`

## Findings

Many `eval`/`exec`/`shell=True`/`pickle` hits live under `theauditor/rules/**` as **detection literals** (the tool hunting those patterns). Those are not automatic self-XSS.

Non-rules `subprocess.*` usage: **33** call sites (venv_install, linters, pipeline, session). That is expected for a meta-tool that shells out to npm, linters, and git. Risk depends on argument construction and `shell=True` (product code hits for shell=True in this scan were mostly rules literals).

`os.system` appears in commands/taint.py and manual_lib01 (needs case-by-case review; not expanded to exploit narrative per policy).

No adversarial pentest was performed. Posture for a local-devtools SAST is broadly "shells out a lot," which is architectural. Highest process risk remains untested publish path, not a specific RCE demo.

Defensive inventory VERIFIED; residual risk judgment INCONCLUSIVE without deeper call-graph review of each subprocess site.

## Verdict

`INCONCLUSIVE`
