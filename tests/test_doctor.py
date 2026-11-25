import json
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

    def tearDown(self):
        self.tmpdir.cleanup()

    def install_harness(self):
        result = self.fx.run("setup")
        self.assertEqual(result.returncode, 0, result.stdout)

    def doctor(self, *args):
        result = self.fx.run("doctor", *args)
        self.assertNotIn(str(self.fx.home), result.stdout)
        return result

    def lines(self, result, status):
        return [line for line in result.stdout.splitlines() if line.startswith(status + " ")]

    def test_installed_machine_passes(self):
        self.install_harness()
        result = self.doctor()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(self.lines(result, "FAIL"), [])
        for line in result.stdout.splitlines():
            self.assertRegex(line, r"^(PASS|WARN|FAIL) [^:]+: ")

    def test_harness_branch_is_reported(self):
        self.install_harness()
        self.assertIn("PASS harness branch: main", self.doctor().stdout.splitlines())
        for command, name in ((("switch", "-q", "-c", "feat/example"), "feat/example"),
                              (("switch", "-q", "--detach"), "a detached HEAD")):
            with self.subTest(name=name):
                subprocess.run(["git", "-C", str(self.fx.harness), *command], env=self.fx.env, check=True)
                result = self.doctor()
                self.assertEqual(result.returncode, 0, result.stdout)
                warnings = [l for l in self.lines(result, "WARN") if l.startswith("WARN harness branch: ")]
                self.assertEqual(len(warnings), 1, result.stdout)
                self.assertTrue(warnings[0].endswith(" is on {}; links into it follow that branch".format(name)))

    def test_setup_repairs_a_moved_installation(self):
        self.install_harness()
        fx = self.fx
        old = fx.harness
        moved = old.with_name("moved")
        backups = fx.home / ".bell-harness/backups"
        original = backups / fx.backups()[0]
        # Restored backup manifests also identify roots, even with damaged lines.
        manifest = original / "manifest.jsonl"
        with manifest.open("ab") as stream:
            stream.write(b"invalid JSON\n[]\n\xff\n")
        original.rename(backups / (original.name + ".restored"))

        stale = fx.home / ".claude/skills/init"
        stale.symlink_to(old / "skills/init")
        retired = fx.home / ".claude/skills/interview"
        retired.symlink_to(old / "skills/interview")
        fx.harness = old.rename(moved)

        result = fx.run("setup")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("replaces the existing entry", result.stdout)
        self.assertIn("unlink ~/.claude/skills/init", result.stdout)
        self.assertIn("unlink ~/.claude/skills/interview", result.stdout)
        self.assertFalse(stale.is_symlink())
        self.assertFalse(retired.is_symlink())
        for name in fx.skill_names:
            for directory in (".claude/skills", ".agents/skills"):
                self.assertEqual((fx.home / directory / name).readlink(), moved / "skills" / name)
        for path, target in (
            (".codex/AGENTS.md", "global/AGENTS.md"),
            (".codex/rules/bell-harness.rules", "config/bell-harness.rules"),
        ):
            self.assertEqual((fx.home / path).readlink(), moved / target)
        repaired = next(backups / name for name in fx.backups() if not name.endswith(".restored"))
        self.assertEqual((repaired / "home/.claude/skills/probe").readlink(), old / "skills/probe")
        self.assertEqual(fx.git("config", "--global", "--get", "core.hooksPath").strip(),
                         str(moved / "git/hooks"))
        result = fx.run("setup")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("setup: nothing to do", result.stdout)

    def test_previous_root_stale_link_matches_setup(self):
        self.install_harness()
        fx = self.fx
        old = fx.harness
        fx.harness = old.rename(old.with_name("moved"))
        repaired = fx.run("setup")
        self.assertEqual(repaired.returncode, 0, repaired.stdout)
        link = fx.home / ".agents/skills/obsolete"
        link.symlink_to(old / "skills/obsolete")
        (link.parent / "foreign").mkdir()

        setup = fx.run("setup", "--dry-run")
        self.assertIn("would unlink ~/.agents/skills/obsolete", setup.stdout)
        result = self.doctor()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL stale link: ~/.agents/skills/obsolete", result.stdout)
        self.assertIn("WARN unmanaged skills: ~/.agents/skills/foreign\n", result.stdout)
        self.assertTrue(link.is_symlink())

    def test_earlier_roots_skip_unsafe_manifests(self):
        self.install_harness()
        fx = self.fx
        backups = fx.home / ".bell-harness/backups"
        outside = fx.tmp / "outside-backup"
        outside.mkdir()
        foreign = fx.tmp / "foreign-harness"
        external = outside / "manifest.jsonl"
        external.write_text(json.dumps({
            "action": "git-config",
            "path": "core.hooksPath",
            "value": str(foreign / "git/hooks"),
            "previous": "absent",
        }) + "\n", encoding="utf-8")

        (backups / "20261122T010102Z").symlink_to(outside, target_is_directory=True)
        backup = backups / "20261122T010101Z.restored"
        backup.mkdir()
        (backup / "manifest.jsonl").symlink_to(external)
        invalid_encoding = backups / "20261122T010100Z"
        invalid_encoding.mkdir()
        (invalid_encoding / "manifest.jsonl").write_bytes(
            external.read_text(encoding="utf-8").strip().encode("utf-16"))
        (fx.home / ".agents/skills/obsolete").symlink_to(foreign / "skills/obsolete")

        result = self.doctor()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("WARN unmanaged skills: ~/.agents/skills/obsolete", result.stdout)
        self.assertNotIn("stale link:", result.stdout)

        relocated = backups.rename(fx.tmp / "relocated-backups")
        (relocated / "20261122T010103Z").mkdir()
        (relocated / "20261122T010103Z/manifest.jsonl").write_bytes(external.read_bytes())
        backups.symlink_to(relocated, target_is_directory=True)
        result = self.doctor()
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("WARN unmanaged skills: ~/.agents/skills/obsolete", result.stdout)
        self.assertNotIn("stale link:", result.stdout)

    def test_broken_link_fails(self):
        self.install_harness()
        os.unlink(str(self.fx.home / ".claude/skills/probe"))
        result = self.doctor()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertTrue(any("~/.claude/skills/probe" in line for line in self.lines(result, "FAIL")),
                        result.stdout)

    def test_leftovers_warn(self):
        self.install_harness()
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

        result = self.doctor("--project-only", str(project))
        self.assertEqual(self.lines(result, "FAIL"), [], result.stdout)
        project_warnings = [line for line in self.lines(result, "WARN")
                            if line.startswith(("WARN project", "WARN stale", "WARN commit", "WARN table"))
                            and "placeholder" not in line]  # this fixture is the template itself
        self.assertEqual(project_warnings, [], result.stdout)
        self.assertIn("PASS table check: table still matches the tree since " + checked_at, result.stdout)

        (project / "docs/plans/second.md").write_text("# Second\n", encoding="utf-8")
        fx.git("add", "docs/plans/second.md", cwd=project)
        fx.git("commit", "-q", "-m", "docs: add the second plan", cwd=project)
        result = self.doctor("--project-only", str(project))
        self.assertIn("PASS table check: table still matches the tree since " + checked_at, result.stdout)
        (project / "docs/notes").mkdir()
        (project / "docs/notes/a.md").write_text("", encoding="utf-8")
        fx.git("add", "docs/notes", cwd=project)
        fx.git("commit", "-q", "-m", "docs: add notes", cwd=project)
        result = self.doctor("--project-only", str(project))
        self.assertIn("PASS table check", result.stdout)
        (project / "plugins/a").mkdir(parents=True)
        (project / "plugins/a/main.py").write_text("", encoding="utf-8")
        fx.git("add", "plugins", cwd=project)
        fx.git("commit", "-q", "-m", "feat: add a plugin", cwd=project)
        result = self.doctor("--project-only", str(project))
        self.assertIn("PASS table check", result.stdout)
        (project / "newarea").mkdir()
        (project / "newarea/tool.py").write_text("", encoding="utf-8")
        fx.git("add", "newarea", cwd=project)
        fx.git("commit", "-q", "-m", "feat: add a new area", cwd=project)
        result = self.doctor("--project-only", str(project))
        self.assertIn("WARN table check: since {}: new folder without a row: newarea; rerun the map skill".format(
            checked_at), result.stdout)

        (project / "helper.py").unlink()
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "--no-verify", "-m", "bad message", cwd=project)
        sha = fx.git("rev-parse", "--short=7", "HEAD", cwd=project).strip()
        result = self.doctor("--project-only", str(project))
        self.assertEqual(self.lines(result, "FAIL"), [], result.stdout)
        warnings = "\n".join(self.lines(result, "WARN"))
        self.assertIn("commit messages: rejected by the harness hook: " + sha, warnings)
        self.assertIn("stale decision: docs/plans/first.md:2: first#D1 cites missing path helper.py", warnings)
        stale_paths = [line for line in self.lines(result, "WARN") if line.startswith("WARN stale table:")]
        self.assertEqual(stale_paths, ['WARN stale table: helper.py (row "<Kind of change>")'], result.stdout)

        agents.write_text(template.replace("<short commit>", "deadbee"), encoding="utf-8")
        self.assertIn("WARN table check: unknown commit deadbee",
                      self.doctor("--project-only", str(project)).stdout)
        agents.write_text(template.replace("Checked at <short commit>\n", ""), encoding="utf-8")
        self.assertIn("WARN table check: no Checked at line (run the map skill)",
                      self.doctor("--project-only", str(project)).stdout)
        agents.unlink()
        result = self.doctor("--project-only", str(project))
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
        result = self.doctor("--project-only", str(project))
        self.assertIn("PASS table check: table still matches the tree since " + parent, result.stdout)
        (project / "helper.py").write_text("a = 3\n", encoding="utf-8")
        fx.git("commit", "-q", "-am", "fix: change the helper", cwd=project)
        result = self.doctor("--project-only", str(project))
        self.assertIn("PASS table check: table still matches the tree since " + parent, result.stdout)
        fx.git("rm", "-q", "helper.py", cwd=project)
        fx.git("commit", "-q", "-m", "refactor: remove the helper", cwd=project)
        result = self.doctor("--project-only", str(project))
        self.assertIn("WARN table check: since {}: removed under a row: helper.py".format(parent), result.stdout)

    def test_project_checks_commit_messages_without_running_local_hook(self):
        self.install_harness()
        fx = self.fx
        project = fx.tmp / "project-only"
        init_repo(project, fx.env)
        fx.git("config", "--global", "core.hooksPath", str(fx.harness / "git/hooks"))
        fx.git("commit", "--allow-empty", "-qm", "bad message", "--no-verify", cwd=project)
        bad = fx.git("rev-parse", "--short=7", "HEAD", cwd=project).strip()
        fx.git("commit", "--allow-empty", "-qm", "test: seed a valid message", cwd=project)
        marker = project / ".git/doctor-hook-ran"
        hook = marker.parent / "hooks/commit-msg"
        hook.write_text("#!/bin/sh\ntouch .git/doctor-hook-ran\n", encoding="utf-8")
        hook.chmod(0o755)

        result = self.doctor("--project", str(project))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("rejected by the harness hook: " + bad, result.stdout)
        self.assertFalse(marker.exists())

        (fx.home / ".codex/AGENTS.md").unlink()
        result = self.doctor("--project-only", str(project))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("rejected by the harness hook: " + bad, result.stdout)
        for prefix in ("PASS prerequisite:", "FAIL link:", "PASS codex mcp:"):
            self.assertNotIn(prefix, result.stdout)
        self.assertFalse(marker.exists())

        result = self.doctor("--project-only", str(project), "--discovery")
        self.assertEqual(result.returncode, 2, result.stdout)

    def test_commit_audit_uses_committed_config_bytes(self):
        fx = self.fx
        project = fx.tmp / "committed-config"
        init_repo(project, fx.env)
        fx.git("config", "--global", "core.hooksPath", str(fx.harness / "git/hooks"))
        config = project / ".harness.json"
        config.write_bytes('{"commit":{"allow_hangul":true}}'.encode("utf-16"))
        fx.git("add", ".harness.json", cwd=project)
        fx.git("commit", "-qm", "test: configure fixture", cwd=project)
        fx.git("commit", "--allow-empty", "-qm", "test: 한글 메시지", cwd=project)
        config.write_text('{"commit":{"allow_hangul":false}}', encoding="utf-8")

        result = self.doctor("--project-only", str(project))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS commit messages: recent commits follow the rules", result.stdout)

    def test_instruction_status_reports_worktree_and_index(self):
        fx = self.fx
        project = fx.tmp / "instruction-status"
        init_repo(project, fx.env)
        agents = project / "AGENTS.md"
        removed = project / "removed" / "CLAUDE.md"
        removed.parent.mkdir()
        agents.write_text("# Project\n", encoding="utf-8")
        removed.write_text("@AGENTS.md\n", encoding="utf-8")
        (project / ".gitignore").write_text("ignored/\n", encoding="utf-8")
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-qm", "docs: seed project instructions", cwd=project)

        agents.write_text("# Staged change\n", encoding="utf-8")
        (project / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        fx.git("add", "AGENTS.md", "CLAUDE.md", cwd=project)
        agents.write_text("# Unstaged change\n", encoding="utf-8")
        removed.unlink()
        for name in ("local notes/AGENTS.md", "ignored/CLAUDE.md", "unrelated.txt"):
            entry = project / name
            entry.parent.mkdir(exist_ok=True)
            entry.write_text("# Test data\n", encoding="utf-8")

        monitor = project / ".git/fsmonitor-test"
        monitor.write_text("#!/bin/sh\n: > .git/fsmonitor-ran\n", encoding="utf-8")
        monitor.chmod(0o755)
        fx.git("config", "core.fsmonitor", str(monitor), cwd=project)

        def snapshot():
            return {
                path.relative_to(project): (path.stat().st_mtime_ns, path.read_bytes())
                for path in project.rglob("*")
                if path.is_file() and ".git" not in path.relative_to(project).parts
            }

        index = project / ".git/index"
        index_before = (index.stat().st_mtime_ns, index.read_bytes())
        worktree_before = snapshot()
        args = ("--project-only", str(project))
        default = self.doctor(*args)
        self.assertEqual(default.returncode, 0, default.stdout)
        self.assertNotIn("untracked instruction", default.stdout)
        self.assertNotIn("uncommitted instruction", default.stdout)

        result = self.doctor(*args, "--instruction-status")
        self.assertEqual(result.returncode, default.returncode, result.stdout)
        self.assertEqual(result.stdout.splitlines(), default.stdout.splitlines() + [
            "WARN uncommitted instruction: 'AGENTS.md' (index=M, worktree=M)",
            "WARN uncommitted instruction: 'CLAUDE.md' (index=A, worktree=.)",
            "WARN untracked instruction: 'local notes/AGENTS.md'",
            "WARN uncommitted instruction: 'removed/CLAUDE.md' (index=., worktree=D)",
        ])
        self.assertEqual((index.stat().st_mtime_ns, index.read_bytes()), index_before)
        self.assertEqual(snapshot(), worktree_before)
        self.assertFalse((project / ".git/fsmonitor-ran").exists())

        fx.git("-c", "core.fsmonitor=false", "add", "-A", cwd=project)
        fx.git("-c", "core.fsmonitor=false", "commit", "-qm", "docs: update project instructions", cwd=project)
        result = self.doctor(*args, "--instruction-status")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("PASS instruction status: no uncommitted instructions", result.stdout)

    def test_instruction_status_handles_unborn_branch_and_unavailable_status(self):
        fx = self.fx
        project = fx.tmp / "unborn"
        init_repo(project, fx.env)
        child = project / "child"
        child.mkdir()
        (child / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        fx.git("add", "child/CLAUDE.md", cwd=project)

        args = ("--project-only", str(project), "--instruction-status")
        result = self.doctor(*args)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("WARN uncommitted instruction: 'child/CLAUDE.md' (index=A, worktree=.)", result.stdout)

        result = self.doctor("--project-only", str(child), "--instruction-status")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("WARN instruction status: use the root of a Git checkout", result.stdout)
        self.assertNotIn("WARN uncommitted instruction:", result.stdout)

        (project / ".git/index").write_bytes(b"broken index")
        result = self.doctor(*args)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("WARN instruction status: could not read Git status", result.stdout)
        self.assertNotIn("PASS instruction status:", result.stdout)

        for unsupported in (("--instruction-status",),
                            ("--project", str(project), "--instruction-status"),
                            args + ("--discovery",)):
            with self.subTest(unsupported=unsupported):
                result = self.doctor(*unsupported)
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_missing_project_directory_fails(self):
        result = self.doctor("--project-only", str(self.fx.tmp / "nope"))
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("FAIL project:", result.stdout)
        self.assertIn("is not a directory", result.stdout)

    def test_project_warns_about_legacy_decisions(self):
        fx = self.fx
        project = fx.tmp / "legacy"
        init_repo(project, fx.env)
        fx.git("config", "--global", "core.hooksPath", str(fx.harness / "git/hooks"))
        plans = project / "docs/plans"
        plans.mkdir(parents=True)
        (plans / "old.md").write_text("## DECIDED\n- D1 (date). Old record\n", encoding="utf-8")
        result = self.doctor("--project-only", str(project))
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn('WARN legacy decisions: docs/plans/old.md has 1 decision-like line(s) '
                      'outside "## Decisions" (run the map skill to migrate)', result.stdout)

    def test_unfilled_template_is_reported(self):
        fx = self.fx
        project = fx.tmp / "unfilled"
        init_repo(project, fx.env)
        fx.git("config", "--file", fx.env["GIT_CONFIG_GLOBAL"], "core.hooksPath", str(fx.harness / "git/hooks"))
        (project / "AGENTS.md").write_text((fx.harness / "templates/AGENTS.md").read_text(encoding="utf-8"),
                                           encoding="utf-8")
        fx.git("add", "-A", cwd=project)
        fx.git("commit", "-q", "-m", "docs: add the agents file", cwd=project)
        result = self.doctor("--project-only", str(project))
        self.assertIn("WARN project AGENTS.md:", result.stdout)
        self.assertIn("template placeholder(s) not filled in", result.stdout)

    def test_discovery(self):
        self.install_harness()
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
        self.install_harness()
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
