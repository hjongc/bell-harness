#!/usr/bin/env python3
"""Decision records in docs/plans/*.md: parse them and report problems.

A record is one line in a spec's `## Decisions` section:
- D<n>: <decision> -- why: <reason> -- by: user|observed [-- paths: <path> ...] [-- supersedes: <slug>#D<n> ...]
"""
import re
import sys
from pathlib import Path


CANDIDATE = re.compile(r"^- D\d")
LEGACY_CANDIDATE = re.compile(r"^- D[0-9]+\b")
FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
SECTION_HEADING = re.compile(r"^ {0,3}#{1,2}[ \t]")
NESTED_ITEM = re.compile(r"^\s+(?:[-*+]|\d+[.)])\s")
HEAD = re.compile(r"^- D([1-9][0-9]*): (\S.*)$")
REF = re.compile(r"^[a-z0-9][a-z0-9.-]*#D[1-9][0-9]*$")
ROADMAP_ITEM = re.compile(r"^- \[( |x)\] ([a-z0-9][a-z0-9.-]*): ")
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


def section_lines(lines, section):
    """Yield numbered lines outside fenced code, with their section membership."""
    in_section = False
    fence = ""
    for number, line in enumerate(lines, 1):
        marker = FENCE.match(line)
        if fence:
            if marker and marker[1].startswith(fence) and not marker[2].strip():
                fence = ""
            continue
        if marker:
            fence = marker[1]
            continue
        if SECTION_HEADING.match(line):
            in_section = line.strip() == section
            continue
        yield number, line, in_section


def parse(text, slug):
    """Parse the `## Decisions` section of one document.

    Returns (decisions, errors); each error is (line number, message).
    """
    decisions, errors = [], []
    lines = text.splitlines()
    for number, line, in_section in section_lines(lines, "## Decisions"):
        if not in_section or not CANDIDATE.match(line):
            continue
        record = line.rstrip()
        for extra in lines[number:]:  # a record may be hard-wrapped onto indented lines
            if (not extra.strip() or not extra[:1].isspace() or NESTED_ITEM.match(extra)
                    or FENCE.match(extra) or SECTION_HEADING.match(extra)):
                break
            record += " " + extra.strip()
        decision, error = _parse_line(slug, number, record)
        if error:
            errors.append((number, error))
        else:
            decisions.append(decision)
    return decisions, errors


def legacy(root):
    """Yield (relative path, count) for decision-like lines outside Decisions."""
    root = Path(root)
    for path in sorted((root / "docs/plans").glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        count = sum(1 for _, line, in_section in section_lines(lines, "## Decisions")
                    if not in_section and LEGACY_CANDIDATE.match(line))
        if count:
            yield path.relative_to(root).as_posix(), count


def table_citation_problems(root, refs, successors):
    agents = root / "AGENTS.md"
    if not agents.is_file():
        return []
    problems = []
    lines = agents.read_text(encoding="utf-8").splitlines()
    for number, raw, in_section in section_lines(lines, "## Sources of truth"):
        line = raw.strip()
        if not in_section or "|" not in line:
            continue
        cells = re.split(r"(?<!\\)\|", line.strip("|"))
        if len(cells) != 3:
            continue
        cited = set(re.findall(r"(?<![\w./-])[a-z0-9][a-z0-9.-]*#D[1-9][0-9]*\b", cells[2]))
        location = "AGENTS.md:{}: ".format(number)
        for ref in sorted(cited):
            if ref not in refs:
                problems.append(location + "unknown decision " + ref)
                continue
            if ref not in successors:
                continue
            active = set()
            pending = [ref]
            visited = set()
            while pending:
                current = pending.pop()
                if current in visited:
                    continue
                visited.add(current)
                if current in successors:
                    pending.extend(successors[current])
                else:
                    active.add(current)
            missing = sorted(active - cited)
            if missing:
                problems.append(location + "{} superseded; cite {}".format(ref, ", ".join(missing)))
            elif not active:
                problems.append(location + ref + " has no active successor")
    return problems


def check(root):
    """Return a list of problems in root/docs/plans/*.md, each 'path:line: message'."""
    root = Path(root)
    plans = root / "docs/plans"
    problems = []
    decisions = []
    for path in sorted(plans.glob("*.md")):
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
    successors = {}
    for decision in decisions:
        for ref in decision.supersedes:
            if ref == decision.ref:
                problems.append("{}:{}: {} supersedes itself".format(
                    decision.source, decision.line, ref))
                continue
            successors.setdefault(ref, set()).add(decision.ref)
            if ref not in refs:
                problems.append("{}:{}: supersedes unknown decision {}".format(
                    decision.source, decision.line, ref))
    for decision in decisions:
        if decision.ref in successors:
            continue
        for item in decision.paths:
            if not (root / item).exists():
                problems.append("{}:{}: {} cites missing path {}".format(
                    decision.source, decision.line, decision.ref, item))

    problems.extend(table_citation_problems(root, refs, successors))
    roadmap = plans / "roadmap.md"
    if roadmap.is_file():
        for number, line in enumerate(roadmap.read_text(encoding="utf-8").splitlines(), 1):
            item = ROADMAP_ITEM.match(line)
            if item:
                slug = item.group(2)
                if not (plans / (slug + ".md")).is_file():
                    problems.append("docs/plans/roadmap.md:{}: unknown spec {}".format(number, slug))
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
