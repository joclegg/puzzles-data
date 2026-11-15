"""Fails if any crossword answer has no clue in crossword/clues.txt.

With --list, prints the missing answers instead, one per line, sorted.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOLDER = ROOT / "crossword"


def answers(line):
    size, solution = line.split(";")
    n = int(size)
    rows = [solution[r * n:(r + 1) * n] for r in range(n)]
    lines = rows + ["".join(row[c] for row in rows) for c in range(n)]
    for text in lines:
        for word in text.split("#"):
            if len(word) > 1:
                yield word


def main():
    clued = set()
    clues = FOLDER / "clues.txt"
    if clues.exists():
        clued = {line.split(";", 1)[0] for line in
                 clues.read_text().splitlines() if line}
    missing = set()
    for name in ("small", "medium", "large"):
        bank = FOLDER / f"{name}.txt"
        if bank.exists():
            for line in bank.read_text().splitlines():
                if line:
                    missing.update(w for w in answers(line) if w not in clued)
    if "--list" in sys.argv:
        print("\n".join(sorted(missing)))
        return 0
    if missing:
        print(f"{len(missing)} crossword answers have no clue, e.g. "
              + ", ".join(sorted(missing)[:10]))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
