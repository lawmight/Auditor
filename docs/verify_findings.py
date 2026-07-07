#!/usr/bin/env python3
"""Rerunnable gate for /docs project-review findings.

Exit 0 only when the Phase A done predicate holds for the docs tree.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

DOCS = Path(__file__).resolve().parent
AGENTS = DOCS / "agents"
REQUIRED_SECTIONS = ("Scope", "Method", "Evidence", "Findings", "Verdict")
VALID_VERDICTS = {"VERIFIED", "NOT VERIFIED", "INCONCLUSIVE"}
EXPECTED = 20


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> None:
    if not (DOCS / "README.md").is_file():
        fail("docs/README.md missing")
    if not (DOCS / "decisions.tsv").is_file():
        fail("docs/decisions.tsv missing")
    if not (DOCS / "PLAYBOOK.md").is_file():
        fail("docs/PLAYBOOK.md missing")

    files = sorted(AGENTS.glob("*.md"))
    if len(files) != EXPECTED:
        fail(f"expected {EXPECTED} agent files, found {len(files)}")

    for i, path in enumerate(files, start=1):
        prefix = f"{i:02d}-"
        if not path.name.startswith(prefix):
            fail(f"{path.name} does not start with {prefix}")
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            if not re.search(rf"^## {re.escape(section)}\s*$", text, re.M):
                fail(f"{path.name} missing section ## {section}")
        m = re.search(r"^## Verdict\s*\n+`?(VERIFIED|NOT VERIFIED|INCONCLUSIVE)`?", text, re.M)
        if not m:
            fail(f"{path.name} Verdict not one of {sorted(VALID_VERDICTS)}")
        if m.group(1) not in VALID_VERDICTS:
            fail(f"{path.name} bad verdict {m.group(1)!r}")

    # decisions.tsv must have header + at least one data row
    rows = (DOCS / "decisions.tsv").read_text(encoding="utf-8").strip().splitlines()
    if len(rows) < 2 or not rows[0].startswith("ts\t"):
        fail("decisions.tsv missing header or rows")

    print(f"PASS: {EXPECTED} findings, sections, verdicts, decisions.tsv OK")


if __name__ == "__main__":
    main()
