"""Merges clue shards from scripts/clues.py into crossword/clues.txt.

Usage: python3 scripts/merge_clues.py DIR
Reads every DIR/*.txt (`WORD;clue` lines) and DIR/*.txt.rejected (one word
per line). Words already clued keep their clue. Both lists stay sorted.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLUES_PATH = ROOT / "crossword" / "clues.txt"
REJECTED_PATH = ROOT / "sources" / "crossword" / "rejected.txt"


def lines(path):
    return [line.strip() for line in path.read_text().splitlines()
            if line.strip()] if path.exists() else []


def main():
    shards = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("out")
    clues = dict(line.split(";", 1) for line in lines(CLUES_PATH))
    rejected = set(lines(REJECTED_PATH))
    for path in sorted(shards.glob("*.txt")):
        for line in lines(path):
            word, clue = line.split(";", 1)
            clues.setdefault(word, clue)
    for path in sorted(shards.glob("*.txt.rejected")):
        rejected.update(lines(path))
    rejected -= clues.keys()

    CLUES_PATH.parent.mkdir(parents=True, exist_ok=True)
    CLUES_PATH.write_text("".join(f"{w};{c}\n" for w, c in sorted(clues.items())))
    REJECTED_PATH.write_text("".join(f"{w}\n" for w in sorted(rejected)))
    print(f"{len(clues)} clued, {len(rejected)} rejected")
    return 0


if __name__ == "__main__":
    sys.exit(main())
