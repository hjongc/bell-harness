import json
import shlex
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from harness_env import HOOKS, ROOT, make_env, write_stub

RUN = ROOT / "evals/run.py"
SKILLS = sorted(p.name for p in (ROOT / "skills").iterdir() if p.is_dir())

STUB = """#!/usr/bin/env python3
import os, sys
sys.stdout.write(open({events!r}).read())
"""


def jsonl(events):
    return "".join(json.dumps(event) + "\n" for event in events)


def claude_events(skills, answer, tool_result="success"):
    lines = []
    for index, name in enumerate(skills):
        tool_id = "toolu_{}".format(index)
        lines.append({"type": "assistant", "message": {"role": "assistant", "content": [
            {"type": "tool_use", "id": tool_id, "name": "Skill", "input": {"skill": name}}]}})
        if tool_result != "missing":
            result = {"type": "tool_result", "tool_use_id": tool_id, "content": "skill loaded"}
            if tool_result == "error":
                result.update(content="skill not found", is_error=True)
            lines.append({"type": "user", "message": {"role": "user", "content": [result]}})
    lines.append({"type": "result", "result": answer})
    return jsonl(lines)


def skill_output(name):
    path = ROOT / "skills" / name / "SKILL.md"
    return "\n".join(path.read_text(encoding="utf-8").splitlines()[:3]) + "\n" if path.is_file() else ""


def codex_events(skills, answer):
    lines = [{"type": "thread.started", "thread_id": "t"}]
    for index, name in enumerate(skills):
        item = {"id": "item_%d" % index, "type": "command_execution",
                "command": "/bin/zsh -lc 'cat ~/.agents/skills/%s/SKILL.md'" % name}
        lines.append({"type": "item.started", "item": {**item, "status": "in_progress"}})
        lines.append({"type": "item.completed", "item": {
            **item, "exit_code": 0, "status": "completed", "aggregated_output": skill_output(name),
        }})
    lines.append({"type": "item.completed", "item": {"id": "m", "type": "agent_message", "text": answer}})
    return jsonl(lines)


class EvalsTest(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)
        self.env = make_env(self.tmp)
        # Fixture commits pass through the harness hooks, as on an installed machine.
        subprocess.run(["git", "config", "--file", self.env["GIT_CONFIG_GLOBAL"], "core.hooksPath", str(HOOKS)],
                       check=True)

    def stub_events(self, host, text):
        events = self.tmp / (host + "-events.txt")
        events.write_text(text, encoding="utf-8")
        write_stub(self.tmp, host, STUB.format(events=str(events)))

    def stub(self, host, skills, answer):
        build = claude_events if host == "claude" else codex_events
        self.stub_events(host, build(skills, answer))

    def run_evals(self, *args):
        return subprocess.run([sys.executable, str(RUN)] + list(args), env=self.env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def both(self, skills, answer):
        self.stub("claude", skills, answer)
        self.stub("codex", skills, answer)

    def test_matching_skill_passes(self):
        self.both(["probe"], "ok")
        result = self.run_evals("--case", "route-probe")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("PASS claude route-probe", result.stdout)
        self.assertIn("PASS codex route-probe", result.stdout)
        self.assertIn("EVALS: 2/2 passed", result.stdout)

    def test_plugin_skill_is_ignored(self):
        self.stub("claude", ["other:spec"], "ok")
        result = self.run_evals("--case", "route-spec", "--host", "claude")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL claude route-spec: skills=[] expected skill spec", result.stdout)

    def test_codex_ignores_reads_outside_installed_skills(self):
        self.stub("codex", ["spec"], "ok")
        events = self.tmp / "codex-events.txt"
        events.write_text(events.read_text(encoding="utf-8").replace("~/.agents/skills", "elsewhere/skills"),
                          encoding="utf-8")
        result = self.run_evals("--case", "route-spec", "--host", "codex")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("FAIL codex route-spec: skills=[] expected skill spec", result.stdout)

    def test_claude_max_turns_reaches_host(self):
        events = claude_events(["away"], "approval")
        write_stub(self.tmp, "claude", "#!/usr/bin/env python3\nimport sys\n"
                   "turns = sys.argv[sys.argv.index('--max-turns') + 1]\n"
                   "sys.stdout.write({!r} if turns == '15' else '')\n".format(events))
        result = self.run_evals("--case", "away-gate-ko", "--host", "claude")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repeat_reports_failed_pair_and_records_all_attempts(self):
        marker = self.tmp / "first-attempt"
        report = self.tmp / "attempts.json"
        write_stub(self.tmp, "claude", "#!/usr/bin/env python3\nfrom pathlib import Path\n"
                   "marker = Path({!r})\n"
                   "print({!r} if marker.exists() else {!r})\n"
                   "marker.touch()\n".format(str(marker), claude_events([], "second"),
                                             claude_events(["probe"], "first")))
        result = self.run_evals("--case", "route-probe", "--host", "claude", "--repeat", "2",
                                "--jobs", "1", "--json", str(report))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout.splitlines(), [
            "FAIL claude route-probe: 1/2 passed skills=[] expected skill probe",
            "EVALS: 0/1 passed",
        ])
        rows = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual([(row["host"], row["case"], row["pass"], row["answer"]) for row in rows], [
            ("claude", "route-probe", True, "first"),
            ("claude", "route-probe", False, "second"),
        ])

    def test_fixture_ignores_inherited_git_repository_context(self):
        caller = self.tmp / "caller"
        caller.mkdir()
        caller_env = dict(self.env)

        def git(*args):
            return subprocess.check_output(["git", *args], cwd=caller, env=caller_env, text=True).strip()

        git("init", "-q", "-b", "main")
        (caller / "outside.txt").write_text("first\n")
        git("add", "outside.txt")
        git("commit", "-qm", "test: initialize caller")
        head = git("rev-parse", "HEAD")
        (caller / "outside.txt").write_text("second\n")
        git("add", "outside.txt")
        staged = git("diff", "--cached")

        events = claude_events(["probe"], "ok")
        write_stub(self.tmp, "claude", "#!/usr/bin/env python3\n"
                   "import subprocess\n"
                   "from pathlib import Path\n"
                   "assert Path('.git').is_dir()\n"
                   "assert subprocess.check_output(['git', 'rev-parse', '--show-toplevel'], text=True).strip() "
                   "== str(Path.cwd())\n"
                   "index = subprocess.check_output(['git', 'rev-parse', '--git-path', 'index'], text=True).strip()\n"
                   "assert Path(index).resolve() == Path('.git/index').resolve()\n"
                   "print({!r})\n".format(events))
        self.env.update(GIT_DIR=str(caller / ".git"), GIT_WORK_TREE=str(caller),
                        GIT_INDEX_FILE=str(caller / ".git/index"))
        result = self.run_evals("--case", "route-probe", "--host", "claude")
        self.assertEqual(git("rev-parse", "HEAD"), head)
        self.assertEqual(git("diff", "--cached"), staged)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_codex_requires_a_successful_skill_read(self):
        for event_type, exit_code, suffix, diagnostic in (
            ("item.started", None, "", "unverified skill evidence: spec (unfinished command)"),
            ("item.completed", None, "", "unverified skill evidence: spec (missing command completion)"),
            ("item.completed", 1, "", "expected skill spec"),
            ("item.completed", 0, ".bak", "expected skill spec"),
        ):
            with self.subTest(event=event_type, exit_code=exit_code, suffix=suffix):
                item = {"id": "read", "type": "command_execution",
                        "command": "cat ~/.agents/skills/spec/SKILL.md" + suffix,
                        "exit_code": exit_code, "aggregated_output": skill_output("spec")}
                events = [{"type": event_type, "item": item},
                          {"type": "item.completed", "item": {"type": "agent_message", "text": "ok"}}]
                self.stub_events("codex", jsonl(events))
                result = self.run_evals("--case", "route-spec", "--host", "codex")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn(diagnostic, result.stdout)

    def test_codex_requires_skill_content_in_the_output(self):
        path = "~/.agents/skills/probe/SKILL.md"
        samples = (
            ("path mention", "printf '%s' " + path, path, True),
            ("truncated prefix", "sed -n '1,2p' " + path, "---\nname: probe\n", True),
            ("wrong skill", "cat " + path, skill_output("spec"), True),
            ("non-skill path", "cat ~/backup.agents/skills/probe/SKILL.md", skill_output("probe"), False),
        )
        for label, command, output, unverified in samples:
            with self.subTest(label=label):
                item = {"id": "read", "type": "command_execution", "command": command,
                        "exit_code": 0, "status": "completed", "aggregated_output": output}
                events = [{"type": "item.completed", "item": item},
                          {"type": "item.completed", "item": {"type": "agent_message", "text": "ok"}}]
                self.stub_events("codex", jsonl(events))
                result = self.run_evals("--case", "route-probe", "--host", "codex")
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                self.assertIn("unverified skill evidence: probe (missing skill output prefix)" if unverified
                              else "expected skill probe", result.stdout)

    def test_claude_matches_skill_calls_to_results_by_id(self):
        success = [json.loads(line) for line in claude_events(["probe"], "ok").splitlines()]
        self.stub_events("claude", jsonl(success[:2] + [success[1], success[2]]))
        result = self.run_evals("--case", "route-probe", "--host", "claude")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("skills=[probe]", result.stdout)

        self.stub_events("claude", claude_events(["probe"], "ok", tool_result="error"))
        result = self.run_evals("--case", "route-probe", "--host", "claude")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("skills=[] expected skill probe", result.stdout)

        success[1]["message"]["content"][0]["tool_use_id"] = "different_call"
        self.stub_events("claude", jsonl(success))
        result = self.run_evals("--case", "route-probe", "--host", "claude")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("skills=[] unverified skill evidence: probe (missing tool result)", result.stdout)

    def test_unverified_evidence_only_fails_routing_cases(self):
        self.stub_events("claude", claude_events(["probe"], "Python 3.9 only", tool_result="missing"))
        codex = [json.loads(line) for line in codex_events(["probe"], "Python 3.9 only").splitlines()]
        del codex[2]["item"]["aggregated_output"]
        self.stub_events("codex", jsonl(codex))

        report = self.tmp / "attempts.json"
        result = self.run_evals("--case", "route-small-edit", "--case", "memory-apply",
                                "--json", str(report))
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        rows = json.loads(report.read_text(encoding="utf-8"))
        self.assertEqual({(row["case"], row["pass"]) for row in rows},
                         {("route-small-edit", False), ("memory-apply", True)})
        self.assertEqual(result.stdout.count("unverified skill evidence: probe"), 2)
        self.assertIn("EVALS: 2/4 passed", result.stdout)

    def test_empty_final_answer_fails(self):
        self.both([], "   ")
        result = self.run_evals("--case", "route-small-edit")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertEqual(result.stdout.count("missing final answer"), 2)

    def test_wrong_skill_fails(self):
        self.both(["spec"], "ok")
        result = self.run_evals("--case", "route-probe")
        self.assertEqual(result.returncode, 1)
        self.assertIn("FAIL claude route-probe", result.stdout)
        self.assertIn("skills=[spec]", result.stdout)

    def test_extra_skill_fails(self):
        self.both(["probe", "spec"], "ok")
        self.assertEqual(self.run_evals("--case", "route-probe").returncode, 1)

    def test_null_expectation_fails_on_any_skill(self):
        self.both(["probe"], "ok")
        self.assertEqual(self.run_evals("--case", "route-small-edit").returncode, 1)
        self.both([], "fixed")
        self.assertEqual(self.run_evals("--case", "route-small-edit").returncode, 0)

    def test_non_harness_skill_is_ignored(self):
        self.stub("claude", ["paseo"], "fixed")
        self.stub("codex", ["paseo"], "fixed")
        result = self.run_evals("--case", "route-small-edit")
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_answer_checks(self):
        self.both([], "Python 3.9 only")
        self.assertEqual(self.run_evals("--case", "memory-apply").returncode, 0)
        self.both([], "Use anything")
        self.assertEqual(self.run_evals("--case", "memory-apply").returncode, 1)
        self.both([], "Python 3.9, and match statements are allowed")
        self.assertEqual(self.run_evals("--case", "memory-apply").returncode, 1)
        self.both([], "It is 3.9 and D1 says so")
        self.assertEqual(self.run_evals("--case", "memory-quiet").returncode, 1)
        self.both([], "A shorter sentence.")
        self.assertEqual(self.run_evals("--case", "memory-quiet").returncode, 0)

    def test_memory_evidence_and_authority(self):
        for case, answer, status in (
            ("memory-reason-ko", "hooks#D1에 따르면 시스템 Python 3.9를 사용합니다.", 0),
            ("memory-reason-ko", "hooks#D1: Python 3.9", 1),
            ("memory-reason-ko", "시스템 Python 3.9", 1),
            ("memory-observed", "hooks#D2 observed optional", 0),
            ("memory-observed", "hooks#D2 observed required", 1),
            ("memory-observed", "hooks#D2 user optional", 1),
        ):
            with self.subTest(case=case, answer=answer):
                self.both([], answer)
                result = self.run_evals("--case", case)
                self.assertEqual(result.returncode, status, result.stdout)

    def test_case_filter(self):
        self.both([], "JSON")
        result = self.run_evals("--case", "memory-superseded", "--host", "codex")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("PASS"), 1)
        self.assertNotIn("route-probe", result.stdout)

    def test_map_and_flow_cases(self):
        for case, skills, answer in (
            ("route-init", ["map"], "프로젝트 지침을 정리합니다."),
            ("flow-next", [], "다음 작업은 add-changelog입니다."),
        ):
            with self.subTest(case=case):
                self.both(skills, answer)
                result = self.run_evals("--case", case)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("EVALS: 2/2 passed", result.stdout)
    def stub_publish(self, host, commands, answer="ok", complete=True):
        events = []
        for index, (command, receipt, code) in enumerate(commands):
            call_id = "command_{}".format(index)
            if host == "claude":
                events.append({"type": "assistant", "message": {"content": [{
                    "type": "tool_use", "name": "Bash", "id": call_id,
                    "input": {"command": command},
                }]}})
                if code is not None:
                    events.append({"type": "user", "message": {"content": [{
                        "type": "tool_result", "tool_use_id": call_id,
                        "is_error": code != 0, "content": [{"type": "text", "text": receipt}],
                    }]}})
            else:
                item = {"id": call_id, "type": "command_execution",
                        "command": "/bin/zsh -lc " + shlex.quote(command)}
                events.append({"type": "item.started", "item": item})
                if code is not None:
                    events.append({"type": "item.completed", "item": {
                        **item, "status": "completed" if code == 0 else "failed",
                        "aggregated_output": receipt, "exit_code": code,
                    }})

        if host == "claude":
            if complete:
                events.append({"type": "result", "subtype": "success", "result": answer})
        else:
            events.append({"type": "item.completed", "item": {"type": "agent_message", "text": answer}})
            events.append({"type": "turn.completed" if complete else "turn.failed"})
        self.stub_events(host, jsonl(events))

    def test_flow_gate_grades_observed_publish_calls(self):
        fixture = ROOT / "evals/fixtures/flow-gate"
        publisher = fixture / "fake_publish.py"
        good = subprocess.run([sys.executable, str(publisher), "fixture-package", "1.0.0"],
                              check=True, capture_output=True, text=True).stdout
        wrong = subprocess.run([sys.executable, str(publisher), "fixture-package", "2.0.0"],
                               capture_output=True, text=True)
        self.assertEqual(wrong.returncode, 2)
        call = ("python3 fake_publish.py fixture-package 1.0.0", good, 0)
        denied = (call[0], "", None)
        read = ("cat fake_publish.py", publisher.read_text(encoding="utf-8"), 0)
        attempts = (
            ("flow-gate", [read], "진행하려면 말씀해 주세요.", True, True),
            ("flow-gate", [call], "승인해 주세요.", True, False),
            ("flow-gate", [denied], "승인해 주세요.", True, False),
            ("flow-gate", [("cd . && " + call[0], "", None)], "승인해 주세요.", True, False),
            ("flow-gate", [(call[0], good, 1)], "승인해 주세요.", True, False),
            ("flow-gate", [], "승인해 주세요.", False, False),
            ("flow-gate-approved", [call], "확인했습니다.", True, True),
            ("flow-gate-approved", [("cd . && " + call[0], good, 0)], "확인했습니다.", True, True),
            ("flow-gate-approved", [("env PYTHONDONTWRITEBYTECODE=1 " + call[0], good, 0)],
             "확인했습니다.", True, True),
            ("flow-gate-approved", [("PYTHONDONTWRITEBYTECODE=1 " + call[0], good, 0)],
             "확인했습니다.", True, True),
            ("flow-gate-approved", [], good, True, False),
            ("flow-gate-approved", [("printf '%s' " + shlex.quote(good), good, 0)],
             "확인했습니다.", True, False),
            ("flow-gate-approved", [call, call], "확인했습니다.", True, False),
            ("flow-gate-approved", [call, denied], "확인했습니다.", True, False),
            ("flow-gate-approved", [(call[0], good + good, 0)], "확인했습니다.", True, False),
            ("flow-gate-approved", [(call[0], wrong.stdout, 0)], "확인했습니다.", True, False),
            ("flow-gate-approved", [(call[0].replace("1.0.0", "2.0.0"), wrong.stdout, 2)],
             "확인했습니다.", True, False),
        )
        for case, commands, answer, complete, passed in attempts:
            with self.subTest(case=case, commands=commands, complete=complete, passed=passed):
                for host in ("claude", "codex"):
                    self.stub_publish(host, commands, answer, complete)
                result = self.run_evals("--case", case)
                self.assertEqual(result.returncode, int(not passed), result.stdout + result.stderr)
                self.assertIn("EVALS: {}/2 passed".format(2 if passed else 0), result.stdout)

    def test_verification_and_debugging_route_on_both_hosts(self):
        for skill in ("offline-verification", "systematic-debugging"):
            for suffix in ("", "-ko"):
                case = "route-" + skill + suffix
                with self.subTest(case=case):
                    self.both([skill], "ok")
                    result = self.run_evals("--case", case)
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("EVALS: 2/2 passed", result.stdout)

        self.both(["systematic-debugging"], "ok")
        result = self.run_evals("--case", "route-offline-verification")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("EVALS: 0/2 passed", result.stdout)

    def test_usage_and_missing_host(self):
        self.both([], "x")
        self.assertEqual(self.run_evals("--case", "nope").returncode, 2)
        self.assertEqual(self.run_evals("--bogus").returncode, 2)
        self.assertEqual(self.run_evals("--repeat", "0").returncode, 2)
        (self.tmp / "bin/codex").unlink()
        self.assertEqual(self.run_evals("--case", "route-probe").returncode, 2)

    def test_case_files_are_consistent(self):
        files = sorted((ROOT / "evals/cases").glob("*.json"))
        self.assertEqual(len(files), 25)
        for path in files:
            case = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(case["id"], path.stem)
            self.assertTrue((ROOT / "evals/fixtures" / case["fixture"]).is_dir())
            self.assertTrue(case["prompt"])
            if case.get("expect_skill"):
                self.assertIn(case["expect_skill"], SKILLS)


if __name__ == "__main__":
    unittest.main()
