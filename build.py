#!/usr/bin/env python3
"""Build the flashcard viewer.

Reads every .md file in the repo (except README.md), turns each
"**Question:**" block into a card, and writes a self-contained static site
to ./_site (index.html + the fi/ image folder).

Usage:  python3 build.py
"""

import hashlib
import json
import re
import shutil
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "_site"

QUESTION_RE = re.compile(r"^\*\*(.+?):\*\*\s*$")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
LECTURE_RE = re.compile(r"^##\s+(.+?)\s*:?\s*$")
TOPIC_RE = re.compile(r"^###\s+(.+?)\s*$")


def unescape(text: str) -> str:
    # Markdown backslash escapes such as "\-" or "\*" -> the bare character.
    return re.sub(r"\\(.)", r"\1", text)


def parse_markdown(text: str, source: str):
    cards = []
    lecture = ""
    topic = ""
    current = None  # the card currently collecting answer lines

    def finish():
        if current is not None:
            current["answer"] = [unescape(l) for l in current["answer_lines"]]
            del current["answer_lines"]
            cards.append(current)

    for raw in text.splitlines():
        line = raw.strip()

        if (m := LECTURE_RE.match(line)) and not line.startswith("###"):
            finish()
            current = None
            lecture, topic = m.group(1), ""
            continue
        if (m := TOPIC_RE.match(line)):
            finish()
            current = None
            topic = m.group(1)
            continue
        if (m := QUESTION_RE.match(line)):
            finish()
            current = {
                "question": unescape(m.group(1)),
                "lecture": lecture,
                "topic": topic,
                "source": source,
                "answer_lines": [],
                "images": [],
            }
            continue
        if current is None or not line:
            continue
        if (m := IMAGE_RE.search(line)):
            current["images"].append(m.group(1))
            continue
        current["answer_lines"].append(line)

    finish()
    return cards


def assign_ids(cards):
    # Stable id = hash of the question text (plus an occurrence counter, so
    # identical questions still get distinct ids). Editing a question's
    # wording therefore clears its mark; reordering does not.
    seen = Counter()
    for card in cards:
        key = card["question"]
        seen[key] += 1
        digest = hashlib.sha1(f"{key}|{seen[key]}".encode("utf-8")).hexdigest()
        card["id"] = digest[:12]
    return cards


def main():
    md_files = sorted(p for p in ROOT.glob("*.md") if p.name.lower() != "readme.md")
    if not md_files:
        raise SystemExit("No .md flashcard files found.")

    cards = []
    for md in md_files:
        cards.extend(parse_markdown(md.read_text(encoding="utf-8"), md.name))
    assign_ids(cards)

    # Warn about images referenced but missing, rather than failing silently.
    missing = sorted({i for c in cards for i in c["images"] if not (ROOT / i).exists()})
    for img in missing:
        print(f"WARNING: image not found: {img}")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)

    images_dir = ROOT / "fi"
    if images_dir.exists():
        shutil.copytree(images_dir, OUT / "fi")

    template = (ROOT / "viewer" / "template.html").read_text(encoding="utf-8")
    # Escape "</" so card text can never close the <script> tag early.
    payload = json.dumps(cards, ensure_ascii=False).replace("</", "<\\/")
    html = template.replace("/*__CARDS__*/[]", payload)
    (OUT / "index.html").write_text(html, encoding="utf-8")

    with_images = sum(1 for c in cards if c["images"])
    print(f"Parsed {len(cards)} cards from {len(md_files)} file(s) "
          f"({with_images} with images).")
    print(f"Site written to {OUT}")


if __name__ == "__main__":
    main()
