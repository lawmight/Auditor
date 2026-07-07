#!/usr/bin/env python3
"""Collect structural evidence for the 20-seam project review.

Writes plain-text artifacts under docs/evidence/ for finding files to cite.
Safe to re-run. Does not mutate product code.
"""

from __future__ import annotations

import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/workspace")
EV = ROOT / "docs" / "evidence"
EV.mkdir(parents=True, exist_ok=True)


def sh(cmd: list[str], cwd: Path = ROOT) -> tuple[int, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=120,
        )
        out = (p.stdout or "") + (("\n" + p.stderr) if p.stderr else "")
        return p.returncode, out
    except Exception as e:  # noqa: BLE001 - evidence collector must not hide probe failures
        return 1, f"ERROR: {e}"


def write(name: str, text: str) -> None:
    (EV / name).write_text(text, encoding="utf-8")
    print(f"wrote {name} ({len(text)} bytes)")


def py_files(base: Path) -> list[Path]:
    skip = {".git", ".venv", ".auditor_venv", "node_modules", "dist", "build", ".pf"}
    out = []
    for p in base.rglob("*.py"):
        if any(part in skip for part in p.parts):
            continue
        out.append(p)
    return out


def loc_by_package() -> None:
    lines = []
    base = ROOT / "theauditor"
    for d in sorted([p for p in base.iterdir() if p.is_dir()]):
        files = list(d.rglob("*.py"))
        n = 0
        for f in files:
            try:
                n += sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
            except OSError:
                pass
        lines.append(f"{d.name}\t{len(files)}\t{n}")
    # top-level py too
    top = list(base.glob("*.py"))
    n = 0
    for f in top:
        n += sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
    lines.insert(0, f"(root)\t{len(top)}\t{n}")
    write("loc_by_package.tsv", "package\tpy_files\tlines\n" + "\n".join(lines) + "\n")


def click_commands() -> None:
    cli = (ROOT / "theauditor" / "cli.py").read_text(encoding="utf-8", errors="replace")
    cmds = sorted(
        set(re.findall(r"(?:@cli\.command\(|@click\.command\(|\.add_command\((\w+))", cli))
    )
    # also scan commands/ for click groups (module stems are the inventory)
    modules = sorted(
        p.stem for p in (ROOT / "theauditor" / "commands").glob("*.py") if p.stem != "__init__"
    )
    write(
        "cli_command_modules.txt",
        "cli.py sequence snippets:\n"
        + "\n".join(str(c) for c in cmds[:50])
        + "\n\ncommand modules:\n"
        + "\n".join(modules)
        + "\n",
    )


def fallback_scan() -> None:
    """Hunt patterns banned by zero-fallback policy (heuristic)."""
    patterns = [
        (r"except\s+Exception\s*:", "bare-except-Exception"),
        (r"except\s*:", "bare-except"),
        (r"if\s+['\"]\w+['\"]\s+in\s+\w*tables", "table-existence-check"),
        (r"hasattr\(", "hasattr"),
        (r"getattr\([^,]+,\s*['\"][^'\"]+['\"]\s*,", "getattr-default"),
        (r"\.get\([^)]+,\s*[^)]+\)\s*(?:or|if)", "dict-get-fallbackish"),
        (r"fall\s*back|fallback", "fallback-word"),
        (r"try:\s*\n(?:.*\n){0,5}.*except.*:\s*\n(?:.*\n){0,3}.*(?:json|JSON|load_from)", "try-except-json-fallback"),
    ]
    counts: Counter[str] = Counter()
    samples: dict[str, list[str]] = defaultdict(list)
    for f in py_files(ROOT / "theauditor"):
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for pat, label in patterns:
            for m in re.finditer(pat, text, re.I | re.M):
                counts[label] += 1
                if len(samples[label]) < 15:
                    # line number
                    line = text[: m.start()].count("\n") + 1
                    rel = f.relative_to(ROOT)
                    samples[label].append(f"{rel}:{line}")
    lines = ["label\tcount\n"] + [f"{k}\t{v}\n" for k, v in sorted(counts.items())]
    write("fallback_heuristic_counts.tsv", "".join(lines))
    sample_lines = []
    for label, locs in sorted(samples.items()):
        sample_lines.append(f"## {label}")
        sample_lines.extend(locs)
        sample_lines.append("")
    write("fallback_heuristic_samples.txt", "\n".join(sample_lines))


def rule_inventory() -> None:
    rules_root = ROOT / "theauditor" / "rules"
    cats = []
    for d in sorted(p for p in rules_root.iterdir() if p.is_dir()):
        py = list(d.rglob("*.py"))
        cats.append(f"{d.name}\t{len(py)}")
    write("rules_categories.tsv", "category\tpy_files\n" + "\n".join(cats) + "\n")
    # METADATA exports
    rc, out = sh(["rg", "-n", r"^METADATA\s*=", "theauditor/rules", "--glob", "*.py"])
    write("rules_metadata_exports.txt", out if out else f"rg_exit={rc}\n")


def test_inventory() -> None:
    # tests may be absent
    test_dirs = []
    for p in ROOT.rglob("test_*.py"):
        if ".git" in p.parts or "node_modules" in p.parts:
            continue
        test_dirs.append(str(p.relative_to(ROOT)))
    for p in ROOT.rglob("*_test.py"):
        if ".git" in p.parts:
            continue
        test_dirs.append(str(p.relative_to(ROOT)))
    # also tests/ folder
    tests_folder = ROOT / "tests"
    listing = ""
    if tests_folder.exists():
        listing = "\n".join(str(p.relative_to(ROOT)) for p in tests_folder.rglob("*.py"))
    write(
        "tests_inventory.txt",
        f"tests_dir_exists={tests_folder.exists()}\n"
        f"test_file_count={len(test_dirs)}\n"
        + "\n".join(sorted(set(test_dirs))[:200])
        + "\n\ntests_folder:\n"
        + listing
        + "\n",
    )


def env_probe() -> None:
    lines = []
    lines.append(f"python3={sys.version}")
    rc, out = sh(["python3", "-c", "import theauditor; print(theauditor.__file__)"])
    lines.append(f"import_theauditor_rc={rc}")
    lines.append(out.strip())
    rc, out = sh(["python3", "-m", "pip", "show", "theauditor"])
    lines.append(f"pip_show_rc={rc}")
    lines.append(out[:500])
    rc, out = sh(["which", "aud"])
    lines.append(f"which_aud={out.strip()} rc={rc}")
    # try install editable minimal?
    write("env_probe.txt", "\n".join(lines) + "\n")


def ci_probe() -> None:
    wf = ROOT / ".github" / "workflows"
    parts = []
    for f in sorted(wf.glob("*.yml")) + sorted(wf.glob("*.yaml")):
        parts.append(f"=== {f.name} ===")
        parts.append(f.read_text(encoding="utf-8", errors="replace")[:4000])
        parts.append("")
    write("ci_workflows.txt", "\n".join(parts) if parts else "NONE\n")


def architecture_inventory() -> None:
    arch = ROOT / "Architecture"
    files = sorted(arch.glob("*.md")) if arch.exists() else []
    lines = [f.name for f in files]
    write("architecture_files.txt", "\n".join(lines) + "\n")
    # compare claimed modules vs folders
    pkgs = sorted(p.name for p in (ROOT / "theauditor").iterdir() if p.is_dir())
    write("theauditor_packages.txt", "\n".join(pkgs) + "\n")


def taint_entry() -> None:
    taint = ROOT / "theauditor" / "taint"
    files = sorted(p.relative_to(ROOT).as_posix() for p in taint.rglob("*.py"))
    write("taint_files.txt", "\n".join(files) + "\n")
    core = taint / "core.py"
    if core.exists():
        text = core.read_text(encoding="utf-8", errors="replace")
        write("taint_core_head.txt", "\n".join(text.splitlines()[:80]) + "\n")


def indexer_entry() -> None:
    idx = ROOT / "theauditor" / "indexer"
    files = sorted(p.relative_to(ROOT).as_posix() for p in idx.rglob("*.py"))
    write("indexer_files.txt", "\n".join(files) + "\n")


def security_sensitive() -> None:
    patterns = [
        r"subprocess\.(run|Popen|call|check_)",
        r"os\.system\(",
        r"eval\(",
        r"exec\(",
        r"pickle\.(loads|load)",
        r"yaml\.load\(",
        r"shell\s*=\s*True",
        r"tempfile\.",
        r"mktemp",
    ]
    samples: dict[str, list[str]] = defaultdict(list)
    counts: Counter[str] = Counter()
    for f in py_files(ROOT / "theauditor"):
        text = f.read_text(encoding="utf-8", errors="replace")
        for pat in patterns:
            for m in re.finditer(pat, text):
                counts[pat] += 1
                if len(samples[pat]) < 10:
                    line = text[: m.start()].count("\n") + 1
                    samples[pat].append(f"{f.relative_to(ROOT)}:{line}")
    lines = ["pattern\tcount\n"] + [f"{k}\t{v}\n" for k, v in sorted(counts.items())]
    write("security_pattern_counts.tsv", "".join(lines))
    out = []
    for pat, locs in sorted(samples.items()):
        out.append(f"## {pat}")
        out.extend(locs)
        out.append("")
    write("security_pattern_samples.txt", "\n".join(out))


def openspec_probe() -> None:
    ospec = ROOT / "openspec"
    if not ospec.exists():
        write("openspec.txt", "missing\n")
        return
    files = sorted(p.relative_to(ROOT).as_posix() for p in ospec.rglob("*") if p.is_file())
    write("openspec.txt", "\n".join(files) + "\n")


def pipeline_probe() -> None:
    p = ROOT / "theauditor" / "pipeline"
    files = sorted(x.relative_to(ROOT).as_posix() for x in p.rglob("*.py"))
    write("pipeline_files.txt", "\n".join(files) + "\n")
    full = ROOT / "theauditor" / "commands" / "full.py"
    if full.exists():
        t = full.read_text(encoding="utf-8", errors="replace")
        write("full_command_head.txt", "\n".join(t.splitlines()[:120]) + "\n")


def framework_probe() -> None:
    for name in ("framework_detector.py", "framework_registry.py", "universal_detector.py"):
        p = ROOT / "theauditor" / name
        if p.exists():
            t = p.read_text(encoding="utf-8", errors="replace")
            write(f"{name}_head.txt", "\n".join(t.splitlines()[:100]) + "\n")
            write(f"{name}_stats.txt", f"lines={len(t.splitlines())}\nbytes={len(t)}\n")


def js_extractor_probe() -> None:
    js = ROOT / "theauditor" / "ast_extractors" / "javascript"
    dist = js / "dist" / "extractor.cjs"
    pkg = js / "package.json"
    lines = [
        f"js_dir_exists={js.exists()}",
        f"dist_exists={dist.exists()}",
        f"dist_size={dist.stat().st_size if dist.exists() else 0}",
        f"package_json={pkg.exists()}",
    ]
    if pkg.exists():
        lines.append(pkg.read_text(encoding="utf-8")[:800])
    write("js_extractor.txt", "\n".join(lines) + "\n")


def readme_pivot_note() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8", errors="replace")
    write("readme_head.txt", "\n".join(readme.splitlines()[:40]) + "\n")
    # pyproject version
    pp = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    m = re.search(r'version\s*=\s*"([^"]+)"', pp)
    req = re.search(r'requires-python\s*=\s*"([^"]+)"', pp)
    write(
        "packaging.txt",
        f"version={m.group(1) if m else '?'}\nrequires-python={req.group(1) if req else '?'}\n",
    )


def main() -> None:
    loc_by_package()
    click_commands()
    fallback_scan()
    rule_inventory()
    test_inventory()
    env_probe()
    ci_probe()
    architecture_inventory()
    taint_entry()
    indexer_entry()
    security_sensitive()
    openspec_probe()
    pipeline_probe()
    framework_probe()
    js_extractor_probe()
    readme_pivot_note()
    print("evidence collection complete")


if __name__ == "__main__":
    main()
