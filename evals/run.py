#!/usr/bin/env python3
"""Live evals: run fixed prompts through the real claude and codex commands.

Each run happens in a temporary copy of a fixture repository. The runner grades
which harness skill was loaded and regular expressions over the final answer.
It calls paid models, so run it by hand (see README.md, "Evals").
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals/cases"
FIXTURES = ROOT / "evals/fixtures"
HOSTS = ("claude", "codex")


def harness_skills():
    return sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())


def load_cases():
    cases = []
    for path in sorted(CASES.glob("*.json")):
        cases.append(json.loads(path.read_text(encoding="utf-8")))
    return cases


def prepare(fixture, tmp):
    """Copy a fixture into tmp and commit it."""
    target = Path(tmp) / "repo"
    shutil.copytree(str(FIXTURES / fixture), str(target))
    git = ["git", "-c", "user.name=Eval", "-c", "user.email=eval@example.com"]
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "chore: add eval fixture"]):
        subprocess.run(git + args, cwd=str(target), check=True, stdout=subprocess.DEVNULL,
                       stderr=subprocess.DEVNULL)
    return target


def json_lines(text):
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if isinstance(event, dict):
            yield event


def parse_claude(text):
    """Return (skills loaded in order, final answer)."""
    skills, answer = [], ""
    for event in json_lines(text):
        if event.get("type") == "assistant":
            content = (event.get("message") or {}).get("content")
            for block in content if isinstance(content, list) else []:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "Skill":
                    name = str((block.get("input") or {}).get("skill", ""))
                    if ":" not in name:
                        skills.append(name)
        elif event.get("type") == "result" and isinstance(event.get("result"), str):
            answer = event["result"]
    return skills, answer


def command_text(command):
    if isinstance(command, list):
        return " ".join(str(part) for part in command)
    return str(command)


def parse_codex(text, names):
    """Return (skills loaded in order, last agent message)."""
    skills, answer, seen = [], "", set()
    for event in json_lines(text):
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        kind = str(item.get("type", ""))
        if "command" in kind and "command" in item:
            command = command_text(item["command"])
            for name in names:
                if ".agents/skills/{}/SKILL.md".format(name) in command and (name, item.get("id")) not in seen:
                    seen.add((name, item.get("id")))
                    skills.append(name)
        elif kind == "agent_message" and isinstance(item.get("text"), str):
            answer = item["text"]
    return skills, answer


def command_for(host, prompt, repo, max_turns=8):
    if host == "claude":
        return ["claude", "-p", prompt, "--output-format", "stream-json", "--verbose",
                "--max-turns", str(max_turns), "--disallowedTools", "Edit", "Write", "NotebookEdit"]
    return ["codex", "exec", "--json", "--skip-git-repo-check", "--ephemeral", "-s", "read-only",
            "-C", str(repo), prompt]


def grade(case, skills, answer):
    """Return None when the run passes, else the failed check."""
    if "expect_skill" in case:
        expected = case["expect_skill"]
        if expected is None:
            if skills:
                return "expected no harness skill"
        elif expected not in skills:
            return "expected skill " + expected
        elif set(skills) != {expected}:
            return "extra harness skill loaded"
    if case.get("expect_answer") and not re.search(case["expect_answer"], answer):
        return "answer missing expect_answer"
    if case.get("reject_answer") and re.search(case["reject_answer"], answer):
        return "answer matches reject_answer"
    return None


def run_one(host, case, timeout):
    names = harness_skills()
    with tempfile.TemporaryDirectory(prefix="harness-eval-") as tmp:
        try:
            repo = prepare(case["fixture"], tmp)
            command = command_for(host, case["prompt"], repo, case.get("max_turns", 8))
            result = subprocess.run(command, cwd=str(repo),
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=timeout)
        except subprocess.TimeoutExpired:
            return host, case["id"], False, "skills=[] timeout after {}s".format(timeout), ""
        except (OSError, subprocess.CalledProcessError) as error:
            return host, case["id"], False, "skills=[] error: {}".format(error), ""
    text = result.stdout.decode("utf-8", "replace")
    if host == "claude":
        skills, answer = parse_claude(text)
    else:
        skills, answer = parse_codex(text, names)
    skills = [name for name in skills if name in names]
    failure = grade(case, skills, answer)
    detail = "skills=[{}]".format(", ".join(skills))
    if failure:
        detail += " " + failure
    elif result.returncode != 0 and not answer:
        failure = "exit {}".format(result.returncode)
        detail += " " + failure
    elif result.returncode != 0:
        # shortcut: a run that answered but exited nonzero (for example at the turn limit) is
        # graded on its answer; make it a failure if such exits start hiding real crashes.
        detail += " (exit {})".format(result.returncode)
    return host, case["id"], failure is None, detail, answer


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run live routing and memory evals.")
    parser.add_argument("--host", choices=HOSTS + ("all",), default="all")
    parser.add_argument("--case", action="append", default=[], dest="cases")
    parser.add_argument("--jobs", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--json", dest="json_path")
    try:
        args = parser.parse_args(argv)
    except SystemExit as error:
        return 2 if error.code else 0
    cases = load_cases()
    known = {case["id"] for case in cases}
    missing = [name for name in args.cases if name not in known]
    if missing or args.jobs < 1:
        print("usage: unknown case {}".format(", ".join(missing)) if missing else "usage: --jobs must be >= 1",
              file=sys.stderr)
        return 2
    if args.repeat < 1:
        print("usage: --repeat must be >= 1", file=sys.stderr)
        return 2
    hosts = HOSTS if args.host == "all" else (args.host,)
    for host in hosts:
        if shutil.which(host) is None:
            print("missing host command: {}".format(host), file=sys.stderr)
            return 2
    jobs = [(host, case) for case in cases if not args.cases or case["id"] in args.cases
            for host in hosts if host in case["hosts"]]
    attempts = [job for job in jobs for _ in range(args.repeat)]
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda job: run_one(job[0], job[1], args.timeout), attempts))
    passed = 0
    for start in range(0, len(results), args.repeat):
        group = results[start:start + args.repeat]
        successful = sum(result[2] for result in group)
        host, case_id, ok, detail, _answer = next((result for result in group if not result[2]), group[0])
        if args.repeat > 1:
            detail = "{}/{} passed {}".format(successful, args.repeat, detail)
        print("{} {} {}: {}".format("PASS" if ok else "FAIL", host, case_id, detail))
        passed += ok
    print("EVALS: {}/{} passed".format(passed, len(jobs)))
    if args.json_path:
        rows = [{"host": h, "case": c, "pass": ok, "detail": d, "answer": a} for h, c, ok, d, a in results]
        Path(args.json_path).write_text(json.dumps(rows, indent=2) + "\n", encoding="utf-8")
    return 0 if passed == len(jobs) else 1


if __name__ == "__main__":
    sys.exit(main())
