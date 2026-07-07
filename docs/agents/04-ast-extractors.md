# Agent 04: AST extractors (polyglot)

## Scope

Inventory language extractors and check README Java / JS-bundle claims against the tree.

## Method

List ast_extractors layout. Inspect JS package.json and dist/extractor.cjs size. Search for java-related paths. Cross-check README pivot claims.

## Evidence

- `docs/evidence/04_extractor_layout.txt`
- `docs/evidence/04_extractor_names.txt`
- `docs/evidence/04_java_hits.txt`
- `docs/evidence/js_extractor.txt`
- `docs/evidence/readme_head.txt`
- `theauditor/ast_extractors/`

## Findings

Extractors exist for Python, JavaScript/TypeScript (TypeScript sources + bundled `dist/extractor.cjs` ~10.3 MB), Go, Rust, Bash, and HCL, plus shared parser helpers.

JS extractor `package.json` builds with esbuild to CJS. Dist artifact is present in-tree, matching hatch force-include in pyproject.

README pivot text claims Java (Maven/Spring/Gradle/Jakarta) is "fully integrated." In this tree, java-named hits are essentially absent (3 path hits, none a Java AST extractor package). Either Java landed only in a closed fork, or the README claim overreaches this snapshot. Treat Java support as **not present here**.

No extractor unit tests were found under a repo `tests/` tree (Agent 17).

Claim-vs-tree gap on Java is the main fidelity finding for this seam.

## Verdict

`VERIFIED`
