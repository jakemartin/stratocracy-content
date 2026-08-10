#!/usr/bin/env python3
"""Rebuild Stratocracy_Prototype_GDD.txt and .pdf from the merged .md.

    python build_docs.py            # rebuild both
    python build_docs.py --txt      # .txt only
    python build_docs.py --pdf      # .pdf only
    python build_docs.py --check    # locate the tools and report, build nothing

Pure standard library. The route is the one CLAUDE.md's merge checklist names and
the one every prior revision was built with: pandoc -s to standalone HTML, then
wkhtmltopdf; .txt via pandoc -t plain.

WHY THIS FILE EXISTS. Neither tool is on PATH on the Director's machine, and a
bare `which wkhtmltopdf` therefore reports it missing when it is installed --
which is how a merge shipped with a stale PDF and a commit message asserting the
tool was absent (content b74a2c1, corrected at e1368bc). The existing PDF had
recorded the answer all along in its own metadata: /Creator wkhtmltopdf 0.12.6.
So this script SEARCHES rather than trusting PATH, and when it fails it prints
every location it looked in.

EXIT CODE IS THE VERDICT. Non-zero if any step fails, and no output file is
replaced unless its build succeeded. The sibling run.py returns 0 even when its
gate BLOCKs; that is a trap for anything automated, and it is not repeated here.

The three files -- .md, .txt, .pdf -- are expected to move together. Rebuild both
after every merge, and check the reported page count against the previous
revision: a large swing means the wrapping or the toolchain moved, not the prose.
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MD = ROOT / "Stratocracy_Prototype_GDD.md"
TXT = ROOT / "Stratocracy_Prototype_GDD.txt"
PDF = ROOT / "Stratocracy_Prototype_GDD.pdf"

# Searched in order. PATH first, then the places each installer actually uses on
# this machine. Add to these lists rather than putting a path in a command.
CANDIDATES = {
    "pandoc": [
        r"C:\Program Files\Pandoc\pandoc.exe",
        r"C:\Users\%USERNAME%\AppData\Local\Pandoc\pandoc.exe",
        "/usr/bin/pandoc",
        "/usr/local/bin/pandoc",
    ],
    "wkhtmltopdf": [
        r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe",
        r"C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe",
        "/usr/bin/wkhtmltopdf",
        "/usr/local/bin/wkhtmltopdf",
    ],
}


def find_tool(name: str) -> str | None:
    """PATH first, then the known install locations. Returns None if unfound."""
    found = shutil.which(name)
    if found:
        return found
    for raw in CANDIDATES[name]:
        p = Path(os.path.expandvars(raw))
        if p.is_file():
            return str(p)
    return None


def searched(name: str) -> str:
    lines = [f"    PATH (shutil.which({name!r}))"]
    lines += [f"    {os.path.expandvars(c)}" for c in CANDIDATES[name]]
    return "\n".join(lines)


def run(cmd: list[str]) -> tuple[bool, str]:
    p = subprocess.run(cmd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return p.returncode == 0, (p.stdout + p.stderr).strip()


def page_count(pdf: Path) -> int:
    """Counts /Type /Page objects. Enough to notice a truncated or empty build."""
    return len(re.findall(rb"/Type\s*/Page[^s]", pdf.read_bytes()))


def build_txt(pandoc: str) -> bool:
    tmp = Path(tempfile.mkdtemp()) / TXT.name
    ok, out = run([pandoc, str(MD), "-t", "plain", "-o", str(tmp)])
    if not ok or not tmp.is_file() or tmp.stat().st_size == 0:
        print(f"[FAIL] .txt not built\n{out}")
        return False
    before = TXT.stat().st_size if TXT.is_file() else 0
    shutil.move(str(tmp), str(TXT))
    print(f"[ok]   .txt  {before} -> {TXT.stat().st_size} bytes")
    return True


def build_pdf(pandoc: str, wk: str) -> bool:
    tmpdir = Path(tempfile.mkdtemp())
    html, tmp = tmpdir / "gdd.html", tmpdir / PDF.name
    ok, out = run([pandoc, str(MD), "-s", "-o", str(html)])
    if not ok or not html.is_file():
        print(f"[FAIL] standalone HTML not built\n{out}")
        return False
    ok, out = run([wk, "--quiet", str(html), str(tmp)])
    if not ok or not tmp.is_file() or tmp.stat().st_size == 0:
        print(f"[FAIL] .pdf not built\n{out}")
        return False
    pages = page_count(tmp)
    if pages == 0:
        print("[FAIL] .pdf has no pages -- refusing to replace the committed one")
        return False
    before = PDF.stat().st_size if PDF.is_file() else 0
    shutil.move(str(tmp), str(PDF))
    print(f"[ok]   .pdf  {before} -> {PDF.stat().st_size} bytes, {pages} pages")
    return True


def main() -> int:
    args = set(sys.argv[1:])
    want_txt = "--pdf" not in args
    want_pdf = "--txt" not in args
    check_only = "--check" in args

    if not MD.is_file():
        print(f"[FAIL] {MD.name} not found beside this script")
        return 1

    pandoc = find_tool("pandoc")
    wk = find_tool("wkhtmltopdf") if (want_pdf or check_only) else None

    print(f"pandoc      : {pandoc or 'NOT FOUND'}")
    print(f"wkhtmltopdf : {wk or 'NOT FOUND'}")

    missing = False
    if pandoc is None:
        print(f"[FAIL] pandoc not found. Searched:\n{searched('pandoc')}")
        missing = True
    if (want_pdf or check_only) and wk is None:
        print(f"[FAIL] wkhtmltopdf not found. Searched:\n{searched('wkhtmltopdf')}")
        print("       Do not conclude it is uninstalled from PATH alone -- the "
              "committed PDF records its builder in /Creator.")
        missing = True
    if missing:
        return 1

    if check_only:
        print("[ok]   --check: tools located, nothing built")
        return 0

    ok = True
    if want_txt:
        ok &= build_txt(pandoc)
    if want_pdf:
        ok &= build_pdf(pandoc, wk)

    print("BUILD PASS" if ok else "BUILD FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
