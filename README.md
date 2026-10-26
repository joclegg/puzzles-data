# puzzle-data

The puzzle banks and word lists shared by [puzzles-android](https://github.com/joclegg/puzzles-android) and [puzzles-web](https://github.com/joclegg/puzzles-web). Both apps include this repository as a git submodule at `puzzle-data/`.

One puzzle per line. Files are plain text.

| Folder | Files | Line format |
| --- | --- | --- |
| `sudoku/` | `<mode>_<level>.txt` | `givens\|solution\|cages`: 81 (or 36) digits each, `0` for an empty given. Killer cages are `sum:cell,cell,...` joined by `;`; empty for classic. |
| `kakuro/` | `<size>.txt` | `size;solution;givens`: the solution row by row, `0` for a black cell, then the given cells as indexes joined by `,`. |
| `slideout/` | `<level>.txt` | `par;blocks`: par is the fewest moves; each block is `row col length H\|V`, the red block first. Levels: beginner 4–9 moves, easy 10–16, medium 17–24, hard 25–32, expert 33–40, evil 41+. |
| `words/` | `answers.txt`, `guesses.txt` | Five Letters: one lowercase word per line. |
| `wordwheel/` | `five.txt`, `six.txt`, `seven.txt`, `valid.txt` | Word Wheel puzzles and the accepted words. See `wordwheel/NOTICE.md`. |

The generators live in puzzles-android (`./gradlew :<game>:engine:generateBank`) and write here.
