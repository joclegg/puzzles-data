# AGENTS.md

The puzzle banks and word lists used by puzzles-android and puzzles-web. See `README.md` for each file's line format.

## Commands

- `python3 scripts/check_duplicates.py`: fail if a bank holds the same puzzle twice, as CI does
- `python3 scripts/manifest.py <path>`: write the manifest of each file's SHA-256 and line count

## Rules

- MUST keep `python3 scripts/check_duplicates.py` passing.
- MUST keep one puzzle per line in plain text, in the format `README.md` gives for that folder.
- MUST NOT edit puzzles by hand: generate them with the generators in puzzles-android (`./gradlew :<game>:engine:generateBank`) or puzzles-web (`scripts/solitaireBank.mjs`).
- MUST NOT reorder or remove lines in a bank without checking the apps first: daily puzzles and saved games can depend on a line's position.
- MUST NOT rename, move or remove a bank file, or change a line format, without updating both apps first: released apps download these files by path.
- MUST add any new top-level bank folder to the copy step in `.github/workflows/publish.yml`, or it won't be published.
- MUST keep `wordwheel/NOTICE.md` with the Word Wheel lists.
- MUST remember that every merge to `main` publishes straight to the apps, with no app release.
