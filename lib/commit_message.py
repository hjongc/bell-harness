"""Shared commit message rules for Git hooks and read-only project diagnostics."""

import json
import re
import unicodedata
from typing import NamedTuple


SUBJECT_PATTERN = r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)(\([^()\s]+\))?!?: \S.*$"
MAX_SUBJECT = 72
EXPECTED_SUBJECT = "type(scope): English imperative summary"
EXEMPT_PREFIXES = ("Merge ", 'Revert "', 'Reapply "', "fixup! ", "squash! ", "amend! ")
HANGUL = re.compile(r"[\u1100-\u11FF\u3131-\u318E\uAC00-\uD7A3]")
ATTRIBUTION = re.compile(r"^co-authored-by:", re.IGNORECASE | re.MULTILINE)


class Policy(NamedTuple):
    pattern: re.Pattern
    max_subject: int
    allow_hangul: bool
    expected: str


def clean_message(text, comment=""):
    if comment in ("", "auto"):
        comment = "#"
    scissors = f"{comment} ------------------------ >8 ------------------------"
    lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line == scissors:
            break
        if not line.startswith(comment):
            lines.append(line)
    return unicodedata.normalize("NFC", "\n".join(lines))


def read_policy(raw):
    """Read the committed configuration, returning None for invalid options."""
    try:
        config = {} if raw is None else json.loads(raw)
        options = config.get("commit", {}) if isinstance(config, dict) else None
        if not isinstance(options, dict):
            return None
        source = options.get("subject_pattern", SUBJECT_PATTERN)
        max_subject = options.get("max_subject", MAX_SUBJECT)
        allow_hangul = options.get("allow_hangul", False)
        if not isinstance(source, str) or type(max_subject) is not int or not isinstance(allow_hangul, bool):
            return None
        expected = options.get("subject_pattern", EXPECTED_SUBJECT)
        return Policy(re.compile(source), max_subject, allow_hangul, expected)
    except (ValueError, re.error, OverflowError):
        return None


def subject_of(message):
    return next((line for line in message.split("\n") if line.strip()), "")


def rejection(message, subject, policy):
    if subject.startswith(EXEMPT_PREFIXES):
        return None
    if not subject:
        return "empty message"
    if policy is None:
        return "invalid .harness.json"
    if not policy.pattern.match(subject):
        return "subject does not match the pattern"
    if len(subject) > policy.max_subject:
        return "subject is too long"
    if not policy.allow_hangul and HANGUL.search(message):
        return "message contains Hangul"
    if ATTRIBUTION.search(message):
        return "Co-Authored-By is not allowed"
    return None
