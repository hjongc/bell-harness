import json
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


def claude_events(skills, answer):
    lines = []
    for name in skills:
        lines.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": name}}]}})
    lines.append({"type": "result", "result": answer})
    return "\n".join(json.dumps(line) for line in lines) + "\n"


def codex_events(skills, answer):
    lines = [{"type": "thread.started", "thread_id": "t"}]
    for index, name in enumerate(skills):
        item = {"id": "item_%d" % index, "type": "command_execution",
                "command": "/bin/zsh -lc 'cat ~/.agents/skills/%s/SKILL.md'" % name}
        lines.append({"type": "item.started", "item": item})
        lines.append({"type": "item.completed", "item": item})
    lines.append({"type": "item.completed", "item": {"id": "m", "type": "agent_message", "text": answer}})
    return "\n".join(json.dumps(line) for line in lines) + "\n"


class EvalsTest(unittest.TestCase):
    def setUp(self):
        holder = tempfile.TemporaryDirectory()
        self.addCleanup(holder.cleanup)
        self.tmp = Path(holder.name)
        self.env = make_env(self.tmp)
        # Fixture commits pass through the harness hooks, as on an installed machine.
        subprocess.run(["git", "config", "--file", self.env["GIT_CONFIG_GLOBAL"], "core.hooksPath", str(HOOKS)],
                       check=True)

    def stub(self, host, skills, answer):
        build = claude_events if host == "claude" else codex_events
        events = self.tmp / (host + "-events.txt")
        events.write_text(build(skills, answer), encoding="utf-8")
        write_stub(self.tmp, host, STUB.format(events=str(events)))

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

    def test_plugin_prefix_is_stripped(self):
        self.both(["x:probe"], "ok")
        self.assertEqual(self.run_evals("--case", "route-probe", "--host", "claude").returncode, 0)

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

    def test_case_filter(self):
        self.both([], "JSON")
        result = self.run_evals("--case", "memory-superseded", "--host", "codex")
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.count("PASS"), 1)
        self.assertNotIn("route-probe", result.stdout)

    def test_usage_and_missing_host(self):
        self.both([], "x")
        self.assertEqual(self.run_evals("--case", "nope").returncode, 2)
        self.assertEqual(self.run_evals("--bogus").returncode, 2)
        (self.tmp / "bin/codex").unlink()
        self.assertEqual(self.run_evals("--case", "route-probe").returncode, 2)

    def test_case_files_are_consistent(self):
        files = sorted((ROOT / "evals/cases").glob("*.json"))
        self.assertEqual(len(files), 8)
        for path in files:
            case = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(case["id"], path.stem)
            self.assertTrue((ROOT / "evals/fixtures" / case["fixture"]).is_dir())
            self.assertTrue(case["prompt"])
            if case.get("expect_skill"):
                self.assertIn(case["expect_skill"], SKILLS)


if __name__ == "__main__":
    unittest.main()
