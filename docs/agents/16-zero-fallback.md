# Agent 16: Zero-fallback policy audit

## Scope

Heuristic scan of theauditor/ for patterns banned or discouraged by CLAUDE.md Zero Fallback law.

## Method

Run regex inventory via collect_evidence fallback_scan: except Exception, bare except, fallback word, hasattr, getattr-default, try/except JSON-ish, table-existence checks.

## Evidence

- `docs/evidence/fallback_heuristic_counts.tsv`
- `docs/evidence/fallback_heuristic_samples.txt`
- `CLAUDE.md`
- `theauditor/taint/`

## Findings

CLAUDE.md bans DB query fallbacks, try/except alternate logic paths, and table-existence prechecks. Taint code loudly asserts NO FALLBACKS.

Heuristic counts across `theauditor/`:

```
label	count
bare-except	1
bare-except-Exception	36
dict-get-fallbackish	266
fallback-word	92
getattr-default	51
hasattr	172
try-except-json-fallback	26
```

Interpretation:
- `except Exception` (36) and try/except-json-ish (26) are smoke signals, not automatic violations. Each needs semantic review.
- `fallback` word hits (92) are often comments documenting the ban, especially in taint.
- `hasattr` (172) and `getattr` with defaults (51) are common Python and not the specific antipatterns called out, but they can hide missing contracts.
- dict-get-fallbackish (266) is a noisy heuristic.

**Conclusion:** Policy is culturally strong in taint/fidelity modules. Repo-wide enforcement is incomplete; automated bans are not encoded as a lint (see encode-lessons principle). No proof of a multi-query DB fallback in this pass, and no proof of cleanliness either.

## Verdict

`INCONCLUSIVE`
