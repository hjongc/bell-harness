#!/usr/bin/env python3
"""Decision records in docs/plans/*.md: parse them and report problems.

A record is one line in a spec's `## Decisions` section:
- D<n>: <decision> -- why: <reason> -- by: user|observed [-- paths: <path> ...] [-- supersedes: <slug>#D<n> ...]
"""
import re
import sys
from pathlib import Path


CANDIDATE = re.compile(r"^- D\d")
HEAD = re.compile(r"^- D([1-9][0-9]*): (\S.*)$")
REF = re.compile(r"^[a-z0-9][a-z0-9.-]*#D[1-9][0-9]*$")
SEPARATOR = " -- "
ORDER = ("why", "by", "paths", "supersedes")
REQUIRED = ("why", "by")
AUTHORS = ("user", "observed")


class Decision(object):
    def __init__(self, slug, number, line, text, fields):
        self.slug = slug
        self.number = number
        self.line = line
        self.text = text
        self.why = fields["why"]
        self.by = fields["by"]
        self.paths = fields.get("paths", "").split()
        self.supersedes = fields.get("supersedes", "").split()

    @property
    def ref(self):
        return "{}#D{}".format(self.slug, self.number)


def _parse_line(slug, number_line, line):
    """Return (Decision, None) or (None, error message)."""
    parts = line.split(SEPARATOR)
    head = HEAD.match(parts[0])
    if not head:
        return None, "expected '- D<n>: <decision>'"
    fields = {}
    last = -1
    for part in parts[1:]:
        key, colon, value = part.partition(": ")
        if not colon or key not in ORDER:
            return None, "unknown field {!r}".format(part.split(":")[0])
        if key in fields:
            return None, "repeated field {!r}".format(key)
        if ORDER.index(key) < last:
            return None, "fields out of order (expected why, by, paths, supersedes)"
        last = ORDER.index(key)
        value = value.strip()
        if not value:
            return None, "empty field {!r}".format(key)
        fields[key] = value
    for key in REQUIRED:
        if key not in fields:
            return None, "missing field {!r}".format(key)
    if fields["by"] not in AUTHORS:
        return None, "by must be 'user' or 'observed'"
    for ref in fields.get("supersedes", "").split():
        if not REF.match(ref):
            return None, "supersedes needs '<slug>#D<n>', got {!r}".format(ref)
    return Decision(slug, int(head.group(1)), number_line, head.group(2), fields), None


def parse(text, slug):
    """Parse the `## Decisions` section of one document.

    Returns (decisions, errors); each error is (line number, message).
    """
    decisions, errors = [], []
    in_section = False
    in_fence = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        if line.startswith("## "):
            in_section = line.strip() == "## Decisions"
            continue
        if not in_section or not CANDIDATE.match(line):
            continue
        decision, error = _parse_line(slug, number, line.rstrip())
        if error:
            errors.append((number, error))
        else:
            decisions.append(decision)
    return decisions, errors


def check(root):
    """Return a list of problems in root/docs/plans/*.md, each 'path:line: message'."""
    root = Path(root)
    problems = []
    decisions = []
    for path in sorted((root / "docs/plans").glob("*.md")):
        name = path.relative_to(root).as_posix()
        found, errors = parse(path.read_text(encoding="utf-8"), path.stem)
        for number, message in errors:
            problems.append("{}:{}: {}".format(name, number, message))
        seen = set()
        for decision in found:
            if decision.number in seen:
                problems.append("{}:{}: duplicate id D{}".format(name, decision.line, decision.number))
            seen.add(decision.number)
            decision.source = name
        decisions.extend(found)

    refs = set(decision.ref for decision in decisions)
    superseded = set()
    for decision in decisions:
        for ref in decision.supersedes:
            superseded.add(ref)
            if ref not in refs:
                problems.append("{}:{}: supersedes unknown decision {}".format(
                    decision.source, decision.line, ref))
    for decision in decisions:
        if decision.ref in superseded:
            continue
        for item in decision.paths:
            if not (root / item).exists():
                problems.append("{}:{}: {} cites missing path {}".format(
                    decision.source, decision.line, decision.ref, item))
    return problems


def main(argv):
    root = Path(argv[1]) if len(argv) > 1 else Path(__file__).resolve().parents[1]
    problems = check(root)
    for problem in problems:
        print("DECISIONS: " + problem)
    if not problems:
        print("DECISIONS: clean")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
