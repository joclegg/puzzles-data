"""Writes quick-crossword clues for the crossword word list with Claude.

Takes every SHARDS-th word of sources/crossword/words.txt, starting at SHARD,
skips words already in crossword/clues.txt or sources/crossword/rejected.txt,
and asks Claude for a clue for each, in batches. Writes `WORD;clue` lines to
OUT and rejected words, one per line, to OUT with `.rejected` added.

Needs ANTHROPIC_API_KEY. Usage:
    python3 scripts/clues.py SHARD SHARDS OUT [--model M] [--effort E]
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS_PATH = ROOT / "sources" / "crossword" / "words.txt"
REJECTED_PATH = ROOT / "sources" / "crossword" / "rejected.txt"
CLUES_PATH = ROOT / "crossword" / "clues.txt"
API_URL = "https://api.anthropic.com/v1/messages"
BATCH = 150

PROMPT = """You are writing clues for a British quick (non-cryptic) crossword \
for a general-audience puzzle app.

For each answer below, write one clue in British English: a short, fair \
definition or synonym that a reasonably well-read adult could solve, usually \
two to six words. Match the answer's form: a plural answer needs a plural \
clue, a past tense a past-tense clue. The clue must not contain the answer, \
or a word sharing its root. Don't add the letter count; the app shows it.

Set keep to false, with an empty clue, for any answer that is obscure, \
archaic, offensive, a slur, sexually explicit, an abbreviation, or that you \
can't clue fairly. Otherwise set keep to true.

Answers:
"""

SCHEMA = {
    "type": "object",
    "properties": {
        "clues": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "keep": {"type": "boolean"},
                    "clue": {"type": "string"},
                },
                "required": ["answer", "keep", "clue"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["clues"],
    "additionalProperties": False,
}


def read_words(path):
    if not path.exists():
        return set()
    return {line.split(";", 1)[0].strip() for line in
            path.read_text().splitlines() if line.strip()}


def ask(words, model, effort, key):
    body = {
        "model": model,
        "max_tokens": 32000,
        "output_config": {
            "effort": effort,
            "format": {"type": "json_schema", "schema": SCHEMA},
        },
        "messages": [{"role": "user",
                      "content": PROMPT + "\n".join(words)}],
    }
    request = urllib.request.Request(
        API_URL, data=json.dumps(body).encode(), method="POST", headers={
            "content-type": "application/json",
            "x-api-key": key,
            "anthropic-version": "2026-10-21",
        })
    for attempt in range(8):
        try:
            with urllib.request.urlopen(request, timeout=600) as response:
                message = json.load(response)
            if message.get("stop_reason") != "end_turn":
                raise ValueError(f"stopped: {message.get('stop_reason')}")
            text = next(b["text"] for b in message["content"]
                        if b["type"] == "text")
            return json.loads(text)["clues"]
        except urllib.error.HTTPError as error:
            if error.code not in (408, 409, 429, 500, 502, 503, 504, 529):
                raise SystemExit(f"API error {error.code}: {error.read()!r}")
            wait = float(error.headers.get("retry-after") or 2 ** attempt)
        except (urllib.error.URLError, TimeoutError, ValueError,
                KeyError, StopIteration) as error:
            print(f"retrying after {error!r}", file=sys.stderr)
            wait = 2 ** attempt
        time.sleep(min(wait, 120))
    raise SystemExit("gave up after repeated API failures")


def valid(word, clue):
    clue = clue.strip()
    return (clue and ";" not in clue and "\n" not in clue
            and word.lower() not in clue.lower() and len(clue) <= 80)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("shard", type=int)
    parser.add_argument("shards", type=int)
    parser.add_argument("out", type=Path)
    parser.add_argument("--model", default="claude-opus-5-5")
    parser.add_argument("--effort", default="medium")
    args = parser.parse_args()
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise SystemExit("ANTHROPIC_API_KEY is not set")

    done = read_words(CLUES_PATH) | read_words(REJECTED_PATH)
    words = sorted(read_words(WORDS_PATH))[args.shard::args.shards]
    todo = [w for w in words if w not in done]
    print(f"shard {args.shard}: {len(todo)} words to clue", file=sys.stderr)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    rejected_out = args.out.with_name(args.out.name + ".rejected")
    with args.out.open("a") as clues, rejected_out.open("a") as rejected:
        for start in range(0, len(todo), BATCH):
            batch = todo[start:start + BATCH]
            wanted = set(batch)
            for item in ask(batch, args.model, args.effort, key):
                word = item["answer"].strip().upper()
                if word not in wanted:
                    continue
                wanted.discard(word)
                if item["keep"] and valid(word, item["clue"]):
                    clues.write(f"{word};{item['clue'].strip()}\n")
                elif not item["keep"]:
                    rejected.write(word + "\n")
            # Words Claude skipped or clued badly are left for the next run.
            clues.flush()
            rejected.flush()
            print(f"shard {args.shard}: {start + len(batch)}/{len(todo)}",
                  file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
