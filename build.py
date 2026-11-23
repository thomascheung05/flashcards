#!/usr/bin/env python3
"""Build the flashcard viewer.

Each course is a folder in the repo that holds one or more .md flashcard
files and, optionally, an fi/ folder with the images they use:

    HENVPaus/
        HENVPaus FlashCards.md
        fi/p02_001.png
    Another Course/
        ...

Every course folder is embedded into a static page at ./_site/index.html,
and each course's fi/ folder is copied to _site/<course>/fi/. The page
shows one tab per course. It parses the markdown itself, so the same code
can also re-parse a file after you edit a card in the browser.

Usage:  python3 build.py
"""

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def find_courses():
    """Folders directly under the repo that contain at least one .md file.

    Hidden folders and folders starting with "_" are skipped, and so is
    viewer/ (it holds the template, not cards).
    """
    courses = []
    for folder in sorted(ROOT.iterdir()):
        if not folder.is_dir() or folder.name.startswith((".", "_")) or folder.name == "viewer":
            continue
        if any(folder.glob("*.md")):
            courses.append(folder)
    return courses


def main():
    courses = find_courses()
    if not courses:
        raise SystemExit("No course folders with .md flashcard files found.")

    sources = []
    for folder in courses:
        for md in sorted(folder.glob("*.md")):
            sources.append({
                "course": folder.name,
                "file": md.name,
                "text": md.read_text(encoding="utf-8"),
            })

    # Warn about images referenced in the markdown but missing from their course folder.
    for src in sources:
        for ref in sorted(set(IMAGE_RE.findall(src["text"]))):
            if not (ROOT / src["course"] / ref).exists():
                print(f"WARNING: image not found in {src['course']}/: {ref}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    for folder in courses:
        if (folder / "fi").exists():
            shutil.copytree(folder / "fi", OUT / folder.name / "fi")

    template = (ROOT / "viewer" / "template.html").read_text(encoding="utf-8")
    # Escape "</" so the card text can never close the <script> tag early.
    payload = json.dumps(sources, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("/*__SOURCES__*/[]", payload)
    (OUT / "index.html").write_text(html, encoding="utf-8")

    names = ", ".join(f.name for f in courses)
    print(f"Embedded {len(sources)} markdown file(s) from {len(courses)} course(s) ({names}) into {OUT / 'index.html'}")


if __name__ == "__main__":
    main()
