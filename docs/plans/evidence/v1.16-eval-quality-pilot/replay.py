"""Replay the original decision parser defect and an ordinary variant."""

import subprocess
import sys
import tempfile
from pathlib import Path


WRAPPED = "- D1: Keep the format -- why: preserve\n  compatibility -- by: observed\n"
CASES = {
    "one-line": "- D1: Keep the format -- why: preserve compatibility -- by: observed\n",
    "wrapped": WRAPPED,
    "nested-notes": (WRAPPED + "  - Check extensions\n  1. Review migration\n"
                     "- D2: Verify locally -- why: reduce retries -- by: observed\n"),
    "missing-by": "- D1: Keep the format -- why: preserve compatibility\n",
}
EXPECTED = {
    "92e3bca": (0, 1, 1, 1),
    "83713c5": (0, 0, 1, 1),
    "3cbb76b": (0, 0, 0, 1),
}


def replay(repo):
    matched = 0
    with tempfile.TemporaryDirectory(prefix="decision-replay-") as temporary:
        for revision, expected_codes in EXPECTED.items():
            source = subprocess.run(
                ["git", "-C", str(repo), "show", revision + ":lib/decisions.py"],
                capture_output=True,
            )
            if source.returncode != 0:
                detail = source.stderr.decode("utf-8", errors="replace").strip()
                print("REPLAY: could not read {}:lib/decisions.py: {}".format(revision, detail),
                      file=sys.stderr)
                return 1

            revision_dir = Path(temporary) / revision
            revision_dir.mkdir()
            script = revision_dir / "decisions.py"
            script.write_bytes(source.stdout)
            for (name, body), expected in zip(CASES.items(), expected_codes):
                project = revision_dir / name
                document = project / "docs" / "plans" / "sample.md"
                document.parent.mkdir(parents=True)
                original = ("## Decisions\n" + body).encode("utf-8")
                document.write_bytes(original)
                result = subprocess.run(
                    [sys.executable, str(script), str(project)],
                    capture_output=True, text=True, encoding="utf-8", errors="replace",
                )
                print("{} {}: exit {} (expected {})".format(revision, name, result.returncode, expected))
                message = (result.stdout + result.stderr).strip()
                print(message or "(no diagnostic)")
                unchanged = document.is_file() and document.read_bytes() == original
                if not unchanged:
                    print("REPLAY: input document changed")
                has_required_diagnostic = name != "missing-by" or "missing field 'by'" in message
                if not has_required_diagnostic:
                    print("REPLAY: missing the required-field diagnostic")
                if result.returncode == expected and unchanged and has_required_diagnostic:
                    matched += 1

    total = len(EXPECTED) * len(CASES)
    print("REPLAY: {}/{} cases matched and kept their input unchanged".format(matched, total))
    return 0 if matched == total else 1


if __name__ == "__main__":
    try:
        raise SystemExit(replay(Path(__file__).resolve().parents[4]))
    except OSError as error:
        print("REPLAY: {}".format(error), file=sys.stderr)
        raise SystemExit(1)
