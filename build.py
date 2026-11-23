#!/usr/bin/env python3
"""Build the flashcard viewer.

Embeds every .md file in the repo (except README.md) into a static page at
./_site/index.html, and copies the fi/ image folder next to it. The page
parses the markdown itself, so the same code can also re-parse a file after
you edit a card in the browser.

Usage:  python3 build.py
"""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def main():
    md_files = sorted(p for p in ROOT.glob("*.md") if p.name.lower() != "readme.md")
    if not md_files:
        raise SystemExit("No .md flashcard files found.")

    sources = [{"file": p.name, "text": p.read_text(encoding="utf-8")} for p in md_files]

    # Warn about images referenced in the markdown but missing from fi/.
    for src in sources:
        for ref in sorted(set(IMAGE_RE.findall(src["text"]))):
            if not (ROOT / ref).exists():
                print(f"WARNING: image not found: {ref}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    if (ROOT / "fi").exists():
        shutil.copytree(ROOT / "fi", OUT / "fi")

    template = (ROOT / "viewer" / "template.html").read_text(encoding="utf-8")
    # Escape "</" so the card text can never close the <script> tag early.
    payload = json.dumps(sources, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("/*__SOURCES__*/[]", payload)
    (OUT / "index.html").write_text(html, encoding="utf-8")

    print(f"Embedded {len(sources)} markdown file(s) into {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
