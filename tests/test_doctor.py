import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from harness_env import init_repo
from test_setup import SKILLS, Fixture


TEMPLATE_DECISIONS = "## Decisions\n- D1: Keep the helper -- why: reused -- by: user -- paths: helper.py\n"


class DoctorTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.fx = Fixture(self.tmpdir.name)
        result = self.fx.run("setup")
        self.assertEqual(result.returncode, 0, result.stdout)

    def tearDown(self):
        self.tmpdir.cleanup()

    def doctor(self, *args):
        result = self.fx.run("doctor", *args)
        self.assertNotIn(str(self.fx.home), result.stdout)
        return result

    def lines(self, result, status):
        return [line for line in result.stdout.splitlines() if line.startswith(status + " ")]

    def test_installed_machine_passes(self):
        result = self.doctor()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.lines(result, "FAIL"), [])
        for line in result.stdout.splitlines():
            self.assertRegex(line, r"^(PASS|WARN|FAIL) [^:]+: ")

    def test_broken_link_fails(self):
        os.unlink(str(self.fx.home / ".claude/skills/probe"))
        result = self.doctor()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertTrue(any("~/.claude/skills/probe" in line for line in self.lines(result, "FAIL")),
                        result.stdout)

    def test_leftovers_warn(self):
        retired = self.fx.home / ".codex/skills/chronicle"
        retired.mkdir(parents=True)
        config = self.fx.home / ".codex/config.toml"
        config.write_text('model_reasoning_effort = "medium"\n\n[profiles.day]\nmodel = "x"\n',
                          encoding="utf-8")
        result = self.doctor()
        self.assertEqual(result.returncode, 0, result.stdout)
        warnings = "\n".join(self.lines(result, "WARN"))
        self.assertIn("retired: ~/.codex/skills/chronicle", warnings)
        self.assertIn("pinned model: ~/.codex/config.toml:4 [profiles.day]", warnings)
        self.assertEqual(warnings.count("pinned model"), 1)

    def test_project_checks(self):
        fx = self.fx
        project = fx.tmp / "project"
        init_repo(project, fx.env)
        fx.git("config", "--file", fx.env["GIT_CONFIG_GLOBAL"], "core.hooksPath", str(fx.harness / "git/hooks"))
        (project / "AGENTS.md").write_text((fx.harness / "templates/AGENTS.md").read_text(encoding="utf-8"),
                                           encoding="utf-8")
        (project / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        (project / "helper.py").write_text("", encoding="utf-8")
        (project / "docs/plans").mkdir(parents=True)
        (project / "docs/plans/first.md").write_text(TEMPLATE_DECISIONS, encoding="utf-8")
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "-m", "feat: start the project", cwd=project)

        result = self.doctor("--project", str(project))
        self.assertEqual(self.lines(result, "FAIL"), [], result.stdout)
        project_warnings = [line for line in self.lines(result, "WARN")
                            if line.startswith(("WARN project", "WARN stale", "WARN commit"))]
        self.assertEqual(project_warnings, [], result.stdout)

        (project / "helper.py").unlink()
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "--no-verify", "-m", "bad message", cwd=project)
        sha = fx.git("rev-parse", "--short=7", "HEAD", cwd=project).strip()
        result = self.doctor("--project", str(project))
        self.assertEqual(self.lines(result, "FAIL"), [], result.stdout)
        warnings = "\n".join(self.lines(result, "WARN"))
        self.assertIn("commit messages: rejected by the harness hook: " + sha, warnings)
        self.assertIn("stale decision: docs/plans/first.md:2: first#D1 cites missing path helper.py", warnings)

    def test_discovery(self):
        result = self.doctor("--discovery")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS claude discovery", result.stdout)
        self.assertIn("PASS codex discovery", result.stdout)

        self.fx.set_discovery(["spec", "taste-skill:brandkit"], ["spec"])
        result = self.doctor("--discovery")
        self.assertEqual(result.returncode, 1, result.stdout)
        fails = "\n".join(self.lines(result, "FAIL"))
        self.assertIn("claude discovery: missing probe, retired taste-skill:brandkit", fails)
        self.assertIn("codex discovery: missing probe", fails)


if __name__ == "__main__":
    unittest.main()
