# -*- coding: utf-8 -*-
"""Render every Month 2 declaration card (days 31-60)."""

import os
import re
import zipfile
from reel_card import render

SRC   = "/home/claude/stories.md"          # extract-text output of the stories docx
THEME = "Marriage & Intimacy"
OUT   = "month2"

# Day 60 is a month-wrap line in the source doc; trimmed to a usable declaration.
OVERRIDES = {60: "The covenant stands."}


def declarations(path, first, last):
    text = open(path).read()
    found = []
    for chunk in re.split(r"## \*\*DAY ", text)[1:]:
        day = int(re.match(r"(\d+)", chunk).group(1))
        if not (first <= day <= last):
            continue
        m = re.search(r"white/gold text:\n\n(.+)", chunk)
        if not m:
            continue
        line = re.sub(r"^Day \d+ of 300\.\s*", "", m.group(1))
        line = re.split(r"📖", line)[0].strip()
        found.append((day, OVERRIDES.get(day, line)))
    return found


def main():
    os.makedirs(OUT, exist_ok=True)
    items = declarations(SRC, 31, 60)

    paths = []
    for day, line in items:
        p = os.path.join(OUT, f"IronAndGrace_Day{day}_Story.png")
        render(line, day, THEME, p)
        paths.append(p)
        print(f"day {day:>3}  {line}")

    zip_path = "IronAndGrace_Month2_Story_Cards.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p, os.path.basename(p))

    print(f"\n{len(paths)} cards -> {zip_path}")


if __name__ == "__main__":
    main()
