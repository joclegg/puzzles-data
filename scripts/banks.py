"""The bank folders the apps download. Kept here once so the scripts and the publish workflow agree."""

# Folders whose .txt files are puzzle banks, one puzzle per line.
PUZZLE_FOLDERS = ("sudoku", "kakuro", "slideout", "solitaire", "wordwheel")
# Everything published, the word lists included.
PUBLISHED_FOLDERS = PUZZLE_FOLDERS + ("words",)

if __name__ == "__main__":
    print(" ".join(PUBLISHED_FOLDERS))
