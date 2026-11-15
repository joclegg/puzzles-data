"""Naive generator for British-style blocked crosswords.

Builds a grid on the usual British lattice (alternate cells in alternate rows
and columns are blocks, so about half the letters are checked), adds blocks
with 180-degree rotational symmetry until no word is too long for the size, then
fills it by backtracking from sources/crossword/words.txt, less the words in
sources/crossword/excluded.txt. Clues are written
separately, into crossword/clues.txt.

Usage: python3 scripts/crossword.py SIZE COUNT [--seed N] [--out PATH]
Appends COUNT new grids to PATH (default crossword/<name>.txt), skipping any
grid already in the file. No word appears in more than --max-uses grids, so
short filler words don't repeat across the bank. Each line is `size;solution`, the solution row by
row with `#` for a block.
"""
import argparse
import random
import sys
from pathlib import Path

MIN_WORD = 3
MAX_WORD = 15
ROOT = Path(__file__).resolve().parent.parent
WORDS_PATH = ROOT / "sources" / "crossword" / "words.txt"
# US spellings, US-only words and anything unsuitable for a family app.
EXCLUDED_PATH = ROOT / "sources" / "crossword" / "excluded.txt"
NAMES = {11: "small", 13: "medium", 15: "large"}
# The longest word each size allows, so grids break up like British ones.
LONGEST = {11: 9, 13: 11, 15: 13}


class Lexicon:
    """Words by length, with a bitmask of word indexes per (length, position, letter)."""

    def __init__(self, words):
        self.words = {}
        self.masks = {}
        for w in sorted(set(words)):
            n = len(w)
            bucket = self.words.setdefault(n, [])
            bit = 1 << len(bucket)
            bucket.append(w)
            for i, ch in enumerate(w):
                key = (n, i, ch)
                self.masks[key] = self.masks.get(key, 0) | bit
        self.full = {n: (1 << len(ws)) - 1 for n, ws in self.words.items()}
        self.index = {w: (len(w), 1 << i) for n, ws in self.words.items()
                      for i, w in enumerate(ws)}
        self.uses = {}

    def use(self, word, cap):
        """Counts a use of word, retiring it once it reaches cap."""
        self.uses[word] = self.uses.get(word, 0) + 1
        if self.uses[word] >= cap and word in self.index:
            n, bit = self.index[word]
            self.full[n] &= ~bit


def load_words():
    words = [w.strip().upper() for w in WORDS_PATH.read_text().splitlines()]
    excluded = set(EXCLUDED_PATH.read_text().split())
    return Lexicon(w for w in words if w not in excluded
                   if w.isalpha() and MIN_WORD <= len(w) <= MAX_WORD)


def slots(grid, size):
    """Every run of two or more white cells, across then down."""
    runs = []
    for across in (True, False):
        for a in range(size):
            run = []
            for b in range(size + 1):
                r, c = (a, b) if across else (b, a)
                if b < size and not grid[r][c]:
                    run.append((r, c))
                else:
                    if len(run) > 1:
                        runs.append(run)
                    run = []
    return runs


def connected(grid, size):
    whites = {(r, c) for r in range(size) for c in range(size)
              if not grid[r][c]}
    start = next(iter(whites))
    seen = {start}
    stack = [start]
    while stack:
        r, c = stack.pop()
        for cell in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
            if cell in whites and cell not in seen:
                seen.add(cell)
                stack.append(cell)
    return len(seen) == len(whites)


def sound(grid, size):
    """No word shorter than MIN_WORD, every white cell in a word, one piece."""
    runs = slots(grid, size)
    if any(len(s) < MIN_WORD for s in runs):
        return False
    covered = {cell for s in runs for cell in s}
    whites = sum(not x for row in grid for x in row)
    return len(covered) == whites and connected(grid, size)


def make_pattern(size, rng):
    """A symmetric lattice grid whose words are all MIN_WORD..LONGEST[size] long."""
    while True:
        # True is a block. Odd rows and odd columns meet at blocks.
        grid = [[r % 2 == 1 and c % 2 == 1 for c in range(size)]
                for r in range(size)]
        while True:
            long_runs = [s for s in slots(grid, size) if len(s) > LONGEST[size]]
            if not long_runs:
                break
            # Try blocking cells of a long word, keeping the first move that
            # leaves a valid grid.
            cells = [cell for run in long_runs
                     for i, cell in enumerate(run)
                     if i >= MIN_WORD and len(run) - i - 1 >= MIN_WORD]
            rng.shuffle(cells)
            for r, c in cells:
                mirror = (size - 1 - r, size - 1 - c)
                grid[r][c] = grid[mirror[0]][mirror[1]] = True
                if sound(grid, size):
                    break
                grid[r][c] = grid[mirror[0]][mirror[1]] = False
            else:
                break
        runs = slots(grid, size)
        if any(not MIN_WORD <= len(s) <= LONGEST[size] for s in runs):
            continue
        # Every white cell must be in a word, and the grid in one piece.
        covered = {cell for s in runs for cell in s}
        whites = {(r, c) for r in range(size) for c in range(size)
                  if not grid[r][c]}
        if covered == whites and connected(grid, size):
            return runs


def fill(size, runs, lex, rng, limit=2000):
    """Backtracking fill, most constrained slot first. None if it gives up."""
    letters = {}
    used = {n: 0 for n in lex.words}
    chosen = [None] * len(runs)
    steps = 0

    def candidates(run):
        n = len(run)
        mask = lex.full.get(n, 0) & ~used[n]
        for i, cell in enumerate(run):
            ch = letters.get(cell)
            if ch:
                mask &= lex.masks.get((n, i, ch), 0)
                if not mask:
                    break
        return mask

    def solve():
        nonlocal steps
        steps += 1
        if steps > limit:
            return False
        best = None
        for k, run in enumerate(runs):
            if chosen[k] is None:
                mask = candidates(run)
                count = mask.bit_count()
                if best is None or count < best[2]:
                    best = (k, mask, count)
                    if not count:
                        return False
        if best is None:
            return True
        k, mask, _ = best
        run = runs[k]
        n = len(run)
        bits = []
        while mask:
            low = mask & -mask
            bits.append(low)
            mask ^= low
        for bit in rng.sample(bits, min(len(bits), 20)):
            word = lex.words[n][bit.bit_length() - 1]
            placed = [cell for cell in run if cell not in letters]
            for i, cell in enumerate(run):
                letters[cell] = word[i]
            used[n] |= bit
            chosen[k] = word
            if solve():
                return True
            chosen[k] = None
            used[n] &= ~bit
            for cell in placed:
                del letters[cell]
        return False

    if not solve():
        return None
    return "".join(letters.get((r, c), "#") for r in range(size)
                   for c in range(size))


def answers(line):
    """The answers in a `size;solution` line."""
    size, solution = line.split(";")
    n = int(size)
    grid = [[solution[r * n + c] == "#" for c in range(n)] for r in range(n)]
    return ["".join(solution[r * n + c] for r, c in run)
            for run in slots(grid, n)]


def load_clues():
    path = ROOT / "crossword" / "clues.txt"
    if not path.exists():
        return {}
    return dict(line.split(";", 1) for line in path.read_text().splitlines()
                if ";" in line)


def clashes(line, clues):
    """True if two answers share a clue, or a clue is another answer."""
    words = answers(line)
    seen = [clues[w].lower() for w in words if w in clues]
    if len(seen) != len(set(seen)):
        return True
    lowered = {w.lower() for w in words}
    return any(clue in lowered for clue in seen)


def generate(size, rng, lex, clues):
    while True:
        solution = fill(size, make_pattern(size, rng), lex, rng)
        if solution and not clashes(f"{size};{solution}", clues):
            return f"{size};{solution}"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("size", type=int, choices=sorted(NAMES))
    parser.add_argument("count", type=int)
    parser.add_argument("--seed", type=int)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--max-uses", type=int,
                        help="most grids one word may appear in, counting "
                        "the grids already in the file (default: 2%% of "
                        "COUNT, at least 5)")
    args = parser.parse_args()

    out = args.out or ROOT / "crossword" / f"{NAMES[args.size]}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    existing = set(out.read_text().splitlines()) if out.exists() else set()
    rng = random.Random(args.seed)
    lex = load_words()
    clues = load_clues()
    cap = args.max_uses or max(5, args.count // 50)
    for line in existing:
        for word in answers(line):
            lex.use(word, cap)

    added = 0
    with out.open("a") as f:
        while added < args.count:
            line = generate(args.size, rng, lex, clues)
            if line in existing:
                continue
            existing.add(line)
            for word in answers(line):
                lex.use(word, cap)
            f.write(line + "\n")
            f.flush()
            added += 1
            if added % 25 == 0:
                print(f"{out}: {added}/{args.count}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
