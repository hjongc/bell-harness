import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from harness_env import init_repo
from test_setup import Fixture


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
        agents = project / "AGENTS.md"
        template = (fx.harness / "templates/AGENTS.md").read_text(encoding="utf-8")
        template = template.replace("<Entry points, tests, data or designs>",
                                    "`<placeholder>`, `*.py`, [helper](helper.py#top), `docs/plans`, "
                                    "[site](https://example.com), [web](http://example.com), "
                                    "[email](mailto:ci@example.com), [heading](#top), [empty](), "
                                    "[placeholder](<placeholder>), [glob](*.py), `plugins/<name>/main.py`")
        agents.write_text(template, encoding="utf-8")
        (project / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        (project / "helper.py").write_text("", encoding="utf-8")
        (project / "docs/plans").mkdir(parents=True)
        (project / "docs/plans/first.md").write_text(TEMPLATE_DECISIONS, encoding="utf-8")
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "-m", "feat: start the project", cwd=project)
        checked_at = fx.git("rev-parse", "--short", "HEAD", cwd=project).strip()
        agents.write_text(template.replace("<short commit>", checked_at), encoding="utf-8")

        result = self.doctor("--project", str(project))
        self.assertEqual(self.lines(result, "FAIL"), [], result.stdout)
        project_warnings = [line for line in self.lines(result, "WARN")
                            if line.startswith(("WARN project", "WARN stale", "WARN commit", "WARN table"))
                            and "placeholder" not in line]  # this fixture is the template itself
        self.assertEqual(project_warnings, [], result.stdout)
        self.assertIn("PASS table check: table still matches the tree since " + checked_at, result.stdout)

        (project / "docs/plans/second.md").write_text("# Second\n", encoding="utf-8")
        fx.git("add", "docs/plans/second.md", cwd=project)
        fx.git("commit", "-q", "-m", "docs: add the second plan", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("PASS table check: table still matches the tree since " + checked_at, result.stdout)
        (project / "docs/notes").mkdir()
        (project / "docs/notes/a.md").write_text("", encoding="utf-8")
        fx.git("add", "docs/notes", cwd=project)
        fx.git("commit", "-q", "-m", "docs: add notes", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("PASS table check", result.stdout)
        (project / "plugins/a").mkdir(parents=True)
        (project / "plugins/a/main.py").write_text("", encoding="utf-8")
        fx.git("add", "plugins", cwd=project)
        fx.git("commit", "-q", "-m", "feat: add a plugin", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("PASS table check", result.stdout)
        (project / "newarea").mkdir()
        (project / "newarea/tool.py").write_text("", encoding="utf-8")
        fx.git("add", "newarea", cwd=project)
        fx.git("commit", "-q", "-m", "feat: add a new area", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("WARN table check: since {}: new folder without a row: newarea; rerun the init skill".format(
            checked_at), result.stdout)

        (project / "helper.py").unlink()
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "--no-verify", "-m", "bad message", cwd=project)
        sha = fx.git("rev-parse", "--short=7", "HEAD", cwd=project).strip()
        result = self.doctor("--project", str(project))
        self.assertEqual(self.lines(result, "FAIL"), [], result.stdout)
        warnings = "\n".join(self.lines(result, "WARN"))
        self.assertIn("commit messages: rejected by the harness hook: " + sha, warnings)
        self.assertIn("stale decision: docs/plans/first.md:2: first#D1 cites missing path helper.py", warnings)
        stale_paths = [line for line in self.lines(result, "WARN") if line.startswith("WARN stale table:")]
        self.assertEqual(stale_paths, ['WARN stale table: helper.py (row "<Kind of change>")'], result.stdout)

        agents.write_text(template.replace("<short commit>", "deadbee"), encoding="utf-8")
        self.assertIn("WARN table check: unknown commit deadbee",
                      self.doctor("--project", str(project)).stdout)
        agents.write_text(template.replace("Checked at <short commit>\n", ""), encoding="utf-8")
        self.assertIn("WARN table check: no Checked at line (run the init skill)",
                      self.doctor("--project", str(project)).stdout)
        agents.unlink()
        result = self.doctor("--project", str(project))
        self.assertNotIn("table check:", result.stdout)
        self.assertNotIn("stale table:", result.stdout)

    def test_table_check_counts_changes_after_the_refresh_commit(self):
        fx = self.fx
        project = fx.tmp / "refresh"
        init_repo(project, fx.env)
        fx.git("config", "--file", fx.env["GIT_CONFIG_GLOBAL"], "core.hooksPath", str(fx.harness / "git/hooks"))
        template = (fx.harness / "templates/AGENTS.md").read_text(encoding="utf-8")
        template = template.replace("<Entry points, tests, data or designs>", "`helper.py`")
        (project / "helper.py").write_text("a = 1\n", encoding="utf-8")
        (project / "AGENTS.md").write_text(template.replace("Checked at <short commit>\n", ""), encoding="utf-8")
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "-m", "feat: start the project", cwd=project)
        parent = fx.git("rev-parse", "--short", "HEAD", cwd=project).strip()
        # One refresh commit changes a table path and records the marker pointing at its parent.
        (project / "helper.py").write_text("a = 2\n", encoding="utf-8")
        (project / "AGENTS.md").write_text(template.replace("<short commit>", parent), encoding="utf-8")
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "-m", "docs: refresh the agents table", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("PASS table check: table still matches the tree since " + parent, result.stdout)
        (project / "helper.py").write_text("a = 3\n", encoding="utf-8")
        fx.git("commit", "-q", "-am", "fix: change the helper", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("PASS table check: table still matches the tree since " + parent, result.stdout)
        fx.git("rm", "-q", "helper.py", cwd=project)
        fx.git("commit", "-q", "-m", "refactor: remove the helper", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("WARN table check: since {}: removed under a row: helper.py".format(parent), result.stdout)

    def test_missing_project_directory_fails(self):
        result = self.doctor("--project", str(self.fx.tmp / "nope"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL project:", result.stdout)
        self.assertIn("is not a directory", result.stdout)

    def test_unfilled_template_is_reported(self):
        fx = self.fx
        project = fx.tmp / "unfilled"
        init_repo(project, fx.env)
        fx.git("config", "--file", fx.env["GIT_CONFIG_GLOBAL"], "core.hooksPath", str(fx.harness / "git/hooks"))
        (project / "AGENTS.md").write_text((fx.harness / "templates/AGENTS.md").read_text(encoding="utf-8"),
                                           encoding="utf-8")
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "-m", "docs: add the agents file", cwd=project)
        result = self.doctor("--project", str(project))
        self.assertIn("WARN project AGENTS.md:", result.stdout)
        self.assertIn("template placeholder(s) not filled in", result.stdout)

    def test_discovery(self):
        result = self.doctor("--discovery")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS claude discovery", result.stdout)
        self.assertIn("PASS codex discovery", result.stdout)

        self.fx.set_discovery(["spec", "taste-skill:brandkit"], ["spec"])
        result = self.doctor("--discovery")
        self.assertEqual(result.returncode, 1, result.stdout)
        fails = "\n".join(self.lines(result, "FAIL"))
        claude_line = [line for line in fails.splitlines() if "claude discovery" in line][0]
        self.assertIn("missing probe", claude_line)
        self.assertNotIn("missing spec", claude_line)
        self.assertIn("retired taste-skill:brandkit", claude_line)
        self.assertIn("codex discovery: missing", fails)


    def test_missing_git_is_reported_not_raised(self):
        only = self.fx.tmp / "only-python"
        only.mkdir()
        os.symlink("/usr/bin/python3", str(only / "python3"))
        env = dict(self.fx.env, PATH=str(only))
        result = subprocess.run([str(self.fx.harness / "bin/doctor")], env=env, cwd=str(self.fx.tmp),
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL prerequisite: git", result.stdout)
        self.assertNotIn("Traceback", result.stdout)


if __name__ == "__main__":
    unittest.main()
