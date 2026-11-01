"""Writes manifest.json: every bank file with its SHA-256 and line count, so apps can download only what changed."""
import hashlib
import json
import sys
from pathlib import Path

from banks import PUBLISHED_FOLDERS


def main(out):
    files = {}
    for folder in PUBLISHED_FOLDERS:
        for path in sorted(Path(folder).glob("*.txt")):
            data = path.read_bytes()
            files[path.as_posix()] = {
                "sha256": hashlib.sha256(data).hexdigest(),
                "lines": sum(1 for line in data.splitlines() if line.strip()),
            }
    Path(out).write_text(json.dumps({"files": files}, indent=1, sort_keys=True))
    print(f"{len(files)} files")


if __name__ == "__main__":
    main(sys.argv[1])
