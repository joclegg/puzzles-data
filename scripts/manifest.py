"""Writes manifest.json: every bank file with its SHA-256 and line count, so apps can download only what changed."""
import hashlib
import json
import os
import sys

out = sys.argv[1]
files = {}
for folder in ("sudoku", "kakuro", "slideout", "solitaire", "wordwheel", "words"):
    for name in sorted(os.listdir(folder)):
        if not name.endswith(".txt"):
            continue
        path = f"{folder}/{name}"
        data = open(path, "rb").read()
        files[path] = {
            "sha256": hashlib.sha256(data).hexdigest(),
            "lines": sum(1 for line in data.splitlines() if line.strip()),
        }
json.dump({"files": files}, open(out, "w"), indent=1, sort_keys=True)
print(f"{len(files)} files")
