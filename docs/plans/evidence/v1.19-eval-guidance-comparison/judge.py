"""Check observable outcomes on the two frozen guidance comparison tasks."""

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def invoke(script, *arguments, cwd):
    return subprocess.run(
        [sys.executable, "-B", str(script), *map(str, arguments)],
        cwd=cwd, capture_output=True, encoding="utf-8", errors="replace", timeout=15,
    )


def preview_checks(source, scratch):
    outside = scratch / "outside"
    outside.mkdir()
    installed = scratch / "installed"
    build = source / "build.py"
    ordinary = invoke(build, installed, cwd=source)
    if ordinary.returncode == 0:
        ordinary = invoke(installed / "preview.py", "Morning notes", cwd=outside)
    yield "ordinary-preview", ordinary.returncode == 0 and ordinary.stdout == "Preview: Morning notes\n", (
        "exit {}, output {!r}".format(ordinary.returncode, ordinary.stdout)
    )

    template = source / "preview.txt"
    installed_text = "Brief: {title}\n"
    template.write_text(installed_text, encoding="utf-8")
    installed = scratch / "installed-variant"
    variant = invoke(build, installed, cwd=source)
    template.write_text("Source only: {title}\n", encoding="utf-8")
    if variant.returncode == 0:
        variant = invoke(installed / "preview.py", "버들", cwd=outside)
    sidecar = installed / "preview.txt"
    preserved = sidecar.is_file() and sidecar.read_text(encoding="utf-8") == installed_text
    yield "different-installed-template", preserved and variant.returncode == 0 and variant.stdout == "Brief: 버들\n", (
        "exit {}, installed template preserved {}, output {!r}".format(variant.returncode, preserved, variant.stdout)
    )

    sidecar.unlink(missing_ok=True)
    missing = invoke(installed / "preview.py", "버들", cwd=outside)
    diagnosed = missing.returncode == 2 and not missing.stdout and "missing installed template" in missing.stderr
    yield "missing-installed-template", diagnosed, (
        "exit {}, output {!r}, error {!r}".format(missing.returncode, missing.stdout, missing.stderr)
    )


def state_bytes(path):
    return path.read_bytes() if path.is_file() else None


def matches_state(path, expected):
    try:
        return json.loads(state_bytes(path)) == expected
    except (TypeError, ValueError):
        return False


def receipt_checks(source, scratch):
    script = source / "receipts.py"
    first = {"id": "demo-21", "message": "첫 메모"}
    second = {"id": "demo-22", "message": "Second note"}
    retry = {"id": first["id"], "message": "Different retry payload"}

    def submit(state, event):
        return invoke(script, state, json.dumps(event, ensure_ascii=False), cwd=source)

    state = scratch / "first.json"
    initial = submit(state, first)
    yield "first-event", initial.returncode == 0 and matches_state(state, [first]), (
        "exit {}, expected one matching receipt".format(initial.returncode)
    )

    state = scratch / "retry.json"
    initial = submit(state, first)
    seeded = initial.returncode == 0 and matches_state(state, [first])
    before = state_bytes(state)
    repeated = submit(state, retry)
    unchanged = state_bytes(state) == before
    yield "repeat-event-id", seeded and repeated.returncode == 0 and unchanged, (
        "exit {}, state bytes unchanged {}".format(repeated.returncode, unchanged)
    )

    state = scratch / "another.json"
    initial = submit(state, first)
    another = submit(state, second)
    yield "different-event-id", initial.returncode == 0 and another.returncode == 0 and matches_state(
        state, [first, second]
    ), "exit {}, expected both receipts in order".format(another.returncode)

    for name, payload in (("malformed-event", "{"), ("invalid-event-schema", '{"id":"","message":"bad"}')):
        state = scratch / (name + ".json")
        initial = submit(state, first)
        seeded = initial.returncode == 0 and matches_state(state, [first])
        before = state_bytes(state)
        invalid = invoke(script, state, payload, cwd=source)
        unchanged = state_bytes(state) == before
        yield name, seeded and invalid.returncode == 2 and "invalid event" in invalid.stderr and unchanged, (
            "exit {}, state bytes unchanged {}".format(invalid.returncode, unchanged)
        )


    absent = scratch / "absent.json"
    invalid = invoke(script, absent, "{", cwd=source)
    yield "invalid-event-keeps-state-absent", invalid.returncode == 2 and "invalid event" in invalid.stderr and not absent.exists(), (
        "exit {}, state absent {}".format(invalid.returncode, not absent.exists())
    )


CHECKS = {"preview": preview_checks, "receipts": receipt_checks}
KNOWN_FAILURES = {
    "preview": {"different-installed-template", "missing-installed-template"},
    "receipts": {"repeat-event-id"},
}


def grade(task, checkout, overlay=None):
    with tempfile.TemporaryDirectory(prefix="guidance-judge-") as temporary:
        scratch = Path(temporary)
        source = scratch / "task"
        shutil.copytree(checkout, source, symlinks=True, ignore=shutil.ignore_patterns(".git"))
        if overlay:
            for path in overlay.iterdir():
                shutil.copyfile(path, source / path.name)
        failures = set()
        for name, passed, detail in CHECKS[task](source, scratch):
            if not passed:
                failures.add(name)
            print("{} {} {}: {}".format("PASS" if passed else "FAIL", task, name, detail))
        return failures


def self_check():
    calibrated = 0
    for task, expected in KNOWN_FAILURES.items():
        checkout = ROOT / "tasks" / task
        for label, overlay, failures in (
            ("known-bad", None, expected),
            ("valid", ROOT / "controls" / task, set()),
        ):
            print("CONTROL {} {}".format(task, label))
            observed = grade(task, checkout, overlay)
            if observed == failures:
                calibrated += 1
            else:
                print("CONTROL mismatch: expected {}, observed {}".format(sorted(failures), sorted(observed)))
    print("JUDGE: {}/4 controls matched".format(calibrated))
    return 0 if calibrated == 4 else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-check", action="store_true", help="compare starters with valid controls")
    parser.add_argument("task", choices=CHECKS, nargs="?")
    parser.add_argument("checkout", type=Path, nargs="?")
    args = parser.parse_args()
    if args.self_check:
        if args.task is not None:
            parser.error("--self-check cannot be combined with a task")
    elif args.checkout is None:
        parser.error("supply a task and checkout, or use --self-check")
    try:
        return self_check() if args.self_check else int(bool(grade(args.task, args.checkout)))
    except (OSError, subprocess.TimeoutExpired) as error:
        print("JUDGE: unavailable: {}".format(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
