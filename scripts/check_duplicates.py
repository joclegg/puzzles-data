"""Fails if any bank holds the same puzzle twice. Slide Out blocks after the red one may be in any order."""
import os
import sys


def key(folder, line):
    if folder == "slideout":
        blocks = line.split(";")[1].split(",")
        return (blocks[0], tuple(sorted(blocks[1:])))
    return line


failed = False
for folder in ("sudoku", "kakuro", "slideout", "solitaire", "wordwheel"):
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".txt") or name == "valid.txt":
            continue
        seen = {}
        for number, line in enumerate(open(os.path.join(folder, name)).read().splitlines(), 1):
            if not line:
                continue
            k = key(folder, line)
            if k in seen:
                print(f"{folder}/{name}:{number} repeats line {seen[k]}")
                failed = True
            else:
                seen[k] = number
sys.exit(1 if failed else 0)
