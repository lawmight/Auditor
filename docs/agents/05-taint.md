# Agent 05: Taint analysis

## Scope

Taint analysis under `theauditor/taint/`. Map IFDS and dual engines, source and sink registry and discovery, and README or Architecture polyglot claims against the package code. Behavioral end-to-end run is out of scope when the CLI cannot import on this host.

## Method

Inventoried nine modules and line counts into `docs/evidence/05_taint_loc.tsv`. Read `core.py` (`trace_taint`, `TaintRegistry`), `ifds_analyzer.py`, `flow_resolver.py`, `discovery.py`, `type_resolver.py`, and `commands/taint.py`. Recounted package keyword hits for IFDS, source, sink, sanitiz, polyglot, classpath. Grepped language extension detection and `NO FALLBACK` / `except Exception`. Compared README polyglot and Java claims to `_get_language_for_file` and Architecture `04_taint.md`.

## Evidence

- `/workspace/docs/evidence/05_taint_loc.tsv`
- `/workspace/docs/evidence/05_taint_module_roles.txt`
- `/workspace/docs/evidence/05_taint_keyword_IFDS.txt` (`count=38`)
- `/workspace/docs/evidence/05_taint_keyword_source.txt` (`count=283`)
- `/workspace/docs/evidence/05_taint_keyword_sink.txt` (`count=356`)
- `/workspace/docs/evidence/05_taint_keyword_sanitiz.txt` (`count=193`)
- `/workspace/docs/evidence/05_taint_keyword_polyglot.txt` (`count=1`)
- `/workspace/docs/evidence/05_taint_keyword_classpath.txt` (`count=0`)
- `/workspace/docs/evidence/05_taint_lang_detect.txt`
- `/workspace/docs/evidence/05_taint_fallback_except.txt`
- `/workspace/docs/evidence/05_readme_polyglot_claims.txt`
- `/workspace/docs/evidence/taint_files.txt`
- `/workspace/docs/evidence/taint_core_head.txt`
- `/workspace/theauditor/taint/core.py`
- `/workspace/theauditor/taint/ifds_analyzer.py`
- `/workspace/theauditor/taint/flow_resolver.py`
- `/workspace/theauditor/taint/discovery.py`
- `/workspace/theauditor/taint/type_resolver.py`
- `/workspace/theauditor/commands/taint.py`
- `/workspace/Architecture/04_taint.md`
- `/workspace/README.md` (polyglot and Java claims)

## Findings

Package size is about 3946 LOC across nine modules. Largest are `core.py` (1057), `flow_resolver.py` (1001), `ifds_analyzer.py` (682), and `discovery.py` (631). Public surface in `__init__.py` exports `trace_taint`, `TaintRegistry`, `IFDSTaintAnalyzer`, `TaintDiscovery`, and `TaintPath`.

Dual engine matches Architecture and CLI `--mode`. `trace_taint` in `core.py` supports `forward` (FlowResolver only), default backward IFDS after discovery, and `complete` (FlowResolver then IFDS with Intersection Strategy on `resolved_flow_audit`). `IFDSTaintAnalyzer` is demand-driven backward worklist from sink access paths with budgets `AUD_IFDS_DEPTH`, `AUD_IFDS_MAX_PATHS`, `AUD_IFDS_BUDGET` (code default 120s; Architecture doc still says 60). Both engines require `graphs.db` and hard-raise if missing (`NO FALLBACKS` messages).

Sources and sinks are registry-driven. `TaintRegistry` keys patterns by language and category, maps sink categories to about eighteen vulnerability type strings, and loads from `framework_taint_patterns`, `framework_safe_sinks`, and `validation_framework_usage`. `TaintDiscovery` finds instances from cache tables (variable usage, symbols, env vars, call args) and classifies via registry. Sanitizer discovery tags validators as `javascript` or `python` explicitly. CLI `aud taint` wraps this as `taint_analyze` with severity filter and mode choice.

Language detection in IFDS and FlowResolver only returns `python`, `javascript` (`.js`/`.ts`/`.jsx`/`.tsx`/`.mjs`/`.cjs`), or `rust`. Other extensions become `unknown`. Zero `.java` or `.go` handling appears under `theauditor/taint/`. The word `classpath` has zero hits in the package. The only `polyglot` hit is the `type_resolver.py` module docstring ("Polyglot Type Identity Checker"); that class resolves ORM model aliases and controller paths from DB metadata, not cross-language taint.

README claims Java fully wired to taint plus "polyglot taint" with multihop, cross-file, and "classpaths". Those claims do not match the taint package as shipped. Cross-file and multihop within the graph-backed engines are real design goals in code. Full polyglot including Java and classpath provenance is not implemented in this tree.

Zero-fallback posture is strong in raises when registry, type resolver, or graphs are missing (13 `NO FALLBACK` sites). `core.py` still has `except Exception` at schema regen (~544, re-raises via `RuntimeError`) and at the end of `trace_taint` (~970, returns `success: False` empty payload). That soft return is a catch-all response path, not an alternate analyzer.

End-to-end taint against a fixture was not run here (CLI import fails on Python 3.12 per agent 01). Structural map and claim-vs-code comparison stand on static evidence.

## Verdict

`VERIFIED`
