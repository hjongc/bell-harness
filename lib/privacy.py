import argparse
import fnmatch
import os
import subprocess
from pathlib import Path

from patterns import EMAIL, EMAIL_ALLOW, HOME_PATHS, SECRET_PATTERNS


def in_git_work_tree(root):
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode == 0 and result.stdout.strip() == b"true"


def git_output(root, *args):
    return subprocess.check_output(["git", *args], cwd=root)


def repository_files(root, in_git):
    if in_git:
        for name in git_output(root, "ls-files", "-co", "--exclude-standard", "-z").split(b"\0"):
            if name:
                yield root / os.fsdecode(name)
        return

    for directory, subdirs, filenames in os.walk(root):
        subdirs[:] = sorted(name for name in subdirs if name not in {".git", ".archive", "__pycache__"})
        for name in sorted(filenames):
            if name != ".private-terms":
                yield Path(directory) / name


def optional_lines(path):
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return []


def file_lines(path):
    # Git records a symlink by its target path.
    if path.is_symlink():
        yield from os.readlink(path).splitlines()
    elif path.is_file():
        with path.open("rb") as stream:
            if b"\0" in stream.read(8192):
                return
            stream.seek(0)
            for line in stream:
                yield line.decode("utf-8", errors="replace")


def kinds_in_line(line, terms):
    # Give the earlier pattern priority when two patterns match the same secret.
    secret_spans = []
    for kind, pattern in SECRET_PATTERNS:
        for match in pattern.finditer(line):
            start, end = match.span()
            if any(
                start < previous_end and previous_start < end
                for previous_start, previous_end in secret_spans
            ):
                continue
            secret_spans.append((start, end))
            yield kind

    for pattern in HOME_PATHS:
        for _ in pattern.finditer(line):
            yield "home-path"
    for match in EMAIL.finditer(line):
        if not match.group().lower().endswith(EMAIL_ALLOW):
            yield "email"
    folded_line = line.casefold()
    for term in terms:
        if term in folded_line:
            yield "private-term"


def scan(root):
    root = Path(root)
    in_git = in_git_work_tree(root)
    terms = [
        line.casefold()
        for raw in optional_lines(root / ".private-terms")
        if (line := raw.strip()) and not line.startswith("#")
    ]
    allow = [line.rsplit(maxsplit=1) for line in optional_lines(root / ".privacy-allow") if line.strip()]
    hits = []
    for path in repository_files(root, in_git):
        relative = path.relative_to(root).as_posix()
        for number, line in enumerate(file_lines(path), 1):
            for kind in kinds_in_line(line, terms):
                if not any(
                    kind == allowed and fnmatch.fnmatchcase(relative, glob)
                    for glob, allowed in allow
                ):
                    hits.append((f"{relative}:{number}", kind))

    if in_git:
        history = git_output(
            root, "log", "--all", "--no-show-signature", "-z", "--format=%h%n%an%n%ae%n%cn%n%ce%n%B"
        )
        for record in history.split(b"\0"):
            if not record:
                continue
            short_hash, _, content = record.decode("utf-8", errors="replace").partition("\n")
            for line in content.splitlines():
                hits.extend((f"commit {short_hash}", kind) for kind in kinds_in_line(line, terms))
    return hits


def main():
    parser = argparse.ArgumentParser(description="Check repository files and history for private data.")
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    hits = scan(parser.parse_args().root)
    for location, kind in hits:
        print(f"PRIVACY: {location}: {kind}")
    if not hits:
        print("PRIVACY: clean")
    return int(bool(hits))


if __name__ == "__main__":
    raise SystemExit(main())
