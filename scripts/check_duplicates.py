"""Fails if any bank holds the same puzzle twice. Slide Out blocks after the red one may be in any order."""
import sys
from pathlib import Path

from banks import PUZZLE_FOLDERS


def key(folder, line):
    if folder == "slideout":
        blocks = line.split(";")[1].split(",")
        return (blocks[0], tuple(sorted(blocks[1:])))
    return line


def main():
    failed = False
    for folder in PUZZLE_FOLDERS:
        for path in sorted(Path(folder).glob("*.txt")):
            if path.name == "valid.txt":
                continue
            seen = {}
            for number, line in enumerate(path.read_text().splitlines(), 1):
                if not line:
                    continue
                k = key(folder, line)
                if k in seen:
                    print(f"{path}:{number} repeats line {seen[k]}")
                    failed = True
                else:
                    seen[k] = number
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
