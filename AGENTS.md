# AGENTS.md

## Structure

The puzzle banks and word lists the Android, iOS and web apps download from https://joclegg.github.io/puzzles-data/. Every file is plain text, one puzzle per line.

| Path | Purpose |
| --- | --- |
| `sudoku/`, `kakuro/`, `slideout/`, `solitaire/`, `wordwheel/` | Puzzle banks, one file per mode or level. |
| `crossword/` | Crossword grids by size and their clues. |
| `words/` | Five Letters' answer and guess lists. |
| `sources/crossword/` | The crossword word list. Not published. |
| `scripts/banks.py` | The list of published folders, used by the other scripts and the publish workflow. |
| `scripts/check_duplicates.py` | Fails if a bank holds the same puzzle twice. |
| `scripts/crossword.py` | Crossword grids, run by `.github/workflows/crossword.yml`. |
| `scripts/check_clues.py` | Fails if a crossword answer has no clue; `--list` prints the missing ones. |
| `scripts/manifest.py` | Writes `manifest.json`: each file's SHA-256 and line count. |
| `.github/workflows/check.yml` | Runs the duplicate and clue checks on every push. |
| `.github/workflows/publish.yml` | Publishes the banks and manifest to GitHub Pages on every merge to `main`. |
| `README.md` | Every file's line format. |

## Conventions

### Checks
- MUST keep `python3 scripts/check_duplicates.py` and `python3 scripts/check_clues.py` passing.
- MUST write scripts in Python 3 with only the standard library, following PEP 8.

### Banks
- MUST keep one puzzle per line in plain text, in the format `README.md` gives for that folder.
- MUST NOT edit puzzles by hand: generate them with the generators in puzzles-android (`./gradlew :<game>:engine:generateBank`) or puzzles-web (`scripts/solitaireBank.mjs`), or for crosswords the Crossword workflow.
- MUST only append to a bank. MUST NOT reorder or remove lines without checking the apps first: daily puzzles and saved games depend on a line's position.
- MUST NOT rename, move or remove a bank file, or change a line format, without updating all three apps first: released apps download these files by path.
- MUST add any new top-level bank folder to `scripts/banks.py`, or it won't be checked or published.
- MUST keep `wordwheel/NOTICE.md` with the Word Wheel lists, and `crossword/NOTICE.md` with the crossword lists.
- MUST keep every crossword answer in `crossword/clues.txt`, one `WORD;clue` line each, sorted: `python3 scripts/check_clues.py` must pass.
- MUST keep `crossword/clues.txt` to British quick-crossword clues: short, fair, matching the answer's form, never containing the answer.
- MUST treat every merge to `main` as a release: it publishes straight to the apps.
