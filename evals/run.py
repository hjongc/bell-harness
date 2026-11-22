#!/usr/bin/env python3
"""Live evals: run fixed prompts through the real claude and codex commands.

Each run happens in a temporary copy of a fixture repository. The runner grades
skill use, final answers, and observed publication actions.
It calls paid models, so run it by hand (see README.md, "Evals").
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from publish_gate import grade_publish_calls


ROOT = Path(__file__).resolve().parents[1]
CASES = ROOT / "evals/cases"
FIXTURES = ROOT / "evals/fixtures"
HOSTS = ("claude", "codex")


def harness_skill_prefixes():
    paths = sorted((ROOT / "skills").glob("*/SKILL.md"))
    return {path.parent.name: path.read_text(encoding="utf-8").splitlines()[:3] for path in paths}


def load_cases():
    cases = []
    for path in sorted(CASES.glob("*.json")):
        cases.append(json.loads(path.read_text(encoding="utf-8")))
    return cases


def fixture_environment():
    # Git exports these variables to hooks. They would redirect fixture and host commands.
    local_names = set(subprocess.check_output(["git", "rev-parse", "--local-env-vars"], text=True).split())
    return {key: value for key, value in os.environ.items() if key not in local_names}


def prepare(fixture, tmp, env):
    """Copy a fixture into tmp and commit it."""
    target = Path(tmp) / "repo"
    shutil.copytree(str(FIXTURES / fixture), str(target))
    git = ["git", "-c", "user.name=Eval", "-c", "user.email=eval@example.com"]
    for args in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-q", "-m", "chore: add eval fixture"]):
        subprocess.run(git + args, cwd=str(target), env=env, check=True, stdout=subprocess.DEVNULL,
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


def parse_claude(text, names):
    """Return verified skills, the final answer, and unresolved evidence."""
    calls, results, unverified = {}, {}, []
    answer = ""
    for event in json_lines(text):
        kind = event.get("type")
        if kind == "result" and isinstance(event.get("result"), str):
            answer = event["result"]
            continue
        message = event.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        for block in content if isinstance(content, list) else ():
            if not isinstance(block, dict):
                continue
            if kind == "assistant" and block.get("type") == "tool_use" and block.get("name") == "Skill":
                inputs = block.get("input")
                name = inputs.get("skill") if isinstance(inputs, dict) else None
                if not isinstance(name, str) or name not in names:
                    continue
                call_id = block.get("id")
                if isinstance(call_id, str) and call_id:
                    calls[call_id] = name
                else:
                    unverified.append((name, "missing tool call ID"))
            elif kind == "user" and block.get("type") == "tool_result":
                call_id = block.get("tool_use_id")
                if isinstance(call_id, str) and call_id in calls:
                    results[call_id] = block.get("is_error", False)

    skills = []
    for call_id, name in calls.items():
        error = results.get(call_id)
        if error is False:
            skills.append(name)
        elif error is not True:
            reason = "invalid tool result" if call_id in results else "missing tool result"
            unverified.append((name, reason))
    return skills, answer, unverified


def command_text(command):
    if isinstance(command, list):
        return " ".join(str(part) for part in command)
    return str(command)


def parse_codex(text, prefixes):
    """Return verified skills, the last agent message, and unresolved evidence."""
    skills, unverified, pending = [], [], {}
    answer = ""
    skill_paths = {
        name: re.compile(r"(?<![\w.-])\.agents/skills/" + re.escape(name) + r"""/SKILL\.md(?=$|[\s'";|&<>()])""")
        for name in prefixes
    }
    for event in json_lines(text):
        kind = event.get("type")
        item = event.get("item")
        if not isinstance(item, dict):
            continue
        if item.get("type") == "agent_message" and kind == "item.completed":
            if isinstance(item.get("text"), str):
                answer = item["text"]
            continue
        if item.get("type") != "command_execution" or kind not in ("item.started", "item.updated", "item.completed"):
            continue
        command = command_text(item.get("command"))
        matches = [name for name, path in skill_paths.items() if path.search(command)]
        raw_id = item.get("id")
        item_id = raw_id if isinstance(raw_id, str) and raw_id else None
        if kind != "item.completed":
            if matches and item_id is not None:
                pending[item_id] = list(dict.fromkeys(pending.get(item_id, []) + matches))
            elif matches:
                unverified.extend((name, "missing command ID") for name in matches)
            continue

        candidates = list(dict.fromkeys(pending.pop(item_id, []) + matches))
        code, status = item.get("exit_code"), item.get("status")
        if status in ("failed", "declined") or (type(code) is int and code != 0):
            continue
        output = item.get("aggregated_output")
        lines = output.splitlines() if isinstance(output, str) else []
        for name in candidates:
            if type(code) is not int or status not in (None, "completed"):
                unverified.append((name, "missing command completion"))
            elif name not in matches:
                unverified.append((name, "missing completed command path"))
            elif len(prefixes[name]) == 3 and any(lines[i:i + 3] == prefixes[name] for i in range(len(lines))):
                skills.append(name)
            else:
                unverified.append((name, "missing skill output prefix"))

    for matches in pending.values():
        unverified.extend((name, "unfinished command") for name in matches)
    return skills, answer, unverified


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


def run_one(host, case, timeout, env, skill_prefixes):
    with tempfile.TemporaryDirectory(prefix="harness-eval-") as tmp:
        try:
            repo = prepare(case["fixture"], tmp, env)
            command = command_for(host, case["prompt"], repo, case.get("max_turns", 8))
            result = subprocess.run(command, cwd=str(repo), env=env,
                                    stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE, timeout=timeout)
        except subprocess.TimeoutExpired:
            return host, case["id"], False, "skills=[] timeout after {}s".format(timeout), ""
        except (OSError, subprocess.CalledProcessError) as error:
            return host, case["id"], False, "skills=[] error: {}".format(error), ""
    text = result.stdout.decode("utf-8", "replace")
    if host == "claude":
        skills, answer, unverified = parse_claude(text, skill_prefixes)
    else:
        skills, answer, unverified = parse_codex(text, skill_prefixes)
    if "expect_skill" in case and unverified:
        evidence = ", ".join("{} ({})".format(name, reason) for name, reason in sorted(set(unverified)))
        failure = "unverified skill evidence: " + evidence
    elif answer.strip():
        failure = grade(case, skills, answer)
        if failure is None and "expect_publish_calls" in case:
            failure = grade_publish_calls(host, json_lines(text), result.returncode, case["expect_publish_calls"])
    else:
        failure = "exit {}".format(result.returncode) if result.returncode else "missing final answer"
    detail = "skills=[{}]".format(", ".join(skills))
    if failure:
        detail += " " + failure
    elif result.returncode != 0:
        # shortcut: a run that answered but exited nonzero (for example at the turn limit) is
        # graded on its answer; make it a failure if such exits start hiding real crashes.
        detail += " (exit {})".format(result.returncode)
    return host, case["id"], failure is None, detail, answer


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run live routing, memory and flow evals.")
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
    try:
        env = fixture_environment()
    except (OSError, subprocess.CalledProcessError) as error:
        print("cannot determine Git repository environment: {}".format(error), file=sys.stderr)
        return 2
    skill_prefixes = harness_skill_prefixes()
    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        results = list(pool.map(lambda job: run_one(job[0], job[1], args.timeout, env, skill_prefixes), attempts))
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
