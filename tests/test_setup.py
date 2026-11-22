import hashlib
import importlib.machinery
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
import unittest
from pathlib import Path

from harness_env import ROOT, make_env, write_stub


RETIRE = json.loads((ROOT / "config/retire.json").read_text(encoding="utf-8"))
FRAGMENT = json.loads((ROOT / "config/claude-settings.json").read_text(encoding="utf-8"))
SKILLS = ("probe", "spec")

CLAUDE_STUB = """#!/usr/bin/env python3
import json, os, sys, time
tmp = {tmp!r}
with open(os.path.join(tmp, "claude-args.log"), "a") as log:
    log.write(json.dumps(sys.argv[1:]) + "\\n")
args = sys.argv[1:]
if args[:1] == ["--version"]:
    print("2.0.0 (Claude Code)")
elif args[:2] == ["plugin", "uninstall"]:
    path = os.path.join(os.environ["HOME"], ".claude/settings.json")
    with open(path) as stream:
        data = json.load(stream)
    data.get("enabledPlugins", {{}}).pop(args[2], None)
    with open(path, "w") as stream:
        json.dump(data, stream, indent=2)
    print("Uninstalled " + args[2])
elif args[:1] == ["plugin"]:
    print("[]")
elif args[:1] == ["-p"]:
    with open(os.path.join(tmp, "claude-skills.json")) as stream:
        skills = json.load(stream)
    print(json.dumps({{"type": "system", "subtype": "hook_started"}}), flush=True)
    print(json.dumps({{"type": "system", "subtype": "init", "skills": skills}}), flush=True)
    time.sleep(60)
"""

CODEX_STUB = """#!/usr/bin/env python3
import os, sys
tmp = {tmp!r}
args = sys.argv[1:]
if args[:2] == ["mcp", "list"]:
    print("Name             Command  Args                    Status")
    print("chrome-devtools  npx      chrome-devtools-mcp@latest  enabled")
    print("playwright       npx      @playwright/mcp@latest  enabled")
elif args[:2] == ["debug", "prompt-input"]:
    with open(os.path.join(tmp, "codex-prompt.txt")) as stream:
        print(stream.read())
elif args[:1] == ["--version"]:
    print("codex-cli 0.0.0")
"""


def copy_harness(destination):
    """Copy the working tree (tracked and untracked, not ignored) into destination."""
    listed = subprocess.run(
        ["git", "ls-files", "-co", "--exclude-standard", "-z"], cwd=ROOT,
        stdout=subprocess.PIPE, check=True).stdout.decode("utf-8").split("\0")
    for name in filter(None, listed):
        source = ROOT / name
        if not os.path.lexists(str(source)):
            continue
        target = destination / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(source), str(target), follow_symlinks=False)


def tree_snapshot(home):
    """Files and links under the managed roots: (path, kind, link target or hash)."""
    snapshot = {}
    for root_name in (".claude", ".agents", ".codex"):
        base = home / root_name
        for folder, dirs, files in os.walk(str(base)):
            for name in dirs + files:
                path = Path(folder) / name
                key = path.relative_to(home).as_posix()
                if key == ".claude/settings.json":
                    continue
                if path.is_symlink():
                    snapshot[key] = ("link", os.readlink(str(path)))
                elif path.is_file():
                    snapshot[key] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
    return snapshot


class Fixture(object):
    def __init__(self, tmp):
        self.tmp = Path(tmp)
        self.env = make_env(self.tmp)
        self.home = Path(self.env["HOME"])
        self.harness = (self.tmp / "harness").resolve()
        self.harness.mkdir()
        copy_harness(self.harness)
        for name in SKILLS:
            skill = self.harness / "skills" / name
            skill.mkdir(parents=True, exist_ok=True)
            (skill / "SKILL.md").write_text("---\nname: {}\n---\n".format(name), encoding="utf-8")
        self.git("init", "-q", "-b", "main", cwd=self.harness)
        self.git("add", "-A", cwd=self.harness)
        self.git("commit", "-q", "-m", "chore: copy harness", cwd=self.harness)
        self.git("config", "--global", "user.name", "Test")
        self.git("config", "--global", "user.email", "test@example.com")
        write_stub(self.tmp, "claude", CLAUDE_STUB.format(tmp=str(self.tmp)))
        write_stub(self.tmp, "codex", CODEX_STUB.format(tmp=str(self.tmp)))
        self.skill_names = sorted(p.name for p in (self.harness / "skills").iterdir()
                                  if (p / "SKILL.md").is_file())
        self.set_discovery(self.skill_names + ["paseo-x"], self.skill_names)
        self.build_home()

    def set_discovery(self, claude_skills, codex_skills):
        (self.tmp / "claude-skills.json").write_text(json.dumps(claude_skills), encoding="utf-8")
        lines = ["{}/skills/{}/SKILL.md".format(self.home / ".agents", n) for n in codex_skills]
        (self.tmp / "codex-prompt.txt").write_text("\n".join(lines), encoding="utf-8")

    def build_home(self):
        home = self.home
        for item in RETIRE["paths"]:
            path = home / item
            path.parent.mkdir(parents=True, exist_ok=True)
            if item.endswith(".md"):
                path.write_text("old command\n", encoding="utf-8")
            else:
                path.mkdir()
                (path / "SKILL.md").write_text("old skill\n", encoding="utf-8")
        old_spec = home / ".claude/skills/spec"
        old_spec.mkdir(parents=True)
        (old_spec / "SKILL.md").write_text("old spec\n", encoding="utf-8")
        foreign = self.tmp / "elsewhere"
        foreign.mkdir()
        (home / ".agents/skills").mkdir(parents=True)
        os.symlink(str(foreign), str(home / ".agents/skills/probe"))
        (home / ".claude/skills/paseo-x").mkdir()
        (home / ".claude/skills/paseo-x/SKILL.md").write_text("paseo\n", encoding="utf-8")
        (home / ".agents/skills/synced").mkdir()
        (home / ".agents/skills/synced/SKILL.md").write_text("synced\n", encoding="utf-8")
        self.settings_before = {
            "hooks": {"Stop": [{"hooks": [{"type": "command", "command": "true"}]}]},
            "enabledPlugins": {"codex@openai-codex": True, "taste-skill@taste-skill": True},
            "theme": "dark",
            "permissions": {"deny": ["Bash(rm -rf:*)"]},
        }
        self.write_settings(self.settings_before)

    def write_settings(self, data):
        path = self.home / ".claude/settings.json"
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def settings(self):
        return json.loads((self.home / ".claude/settings.json").read_text(encoding="utf-8"))

    def git(self, *args, cwd=None):
        return subprocess.run(["git"] + list(args), cwd=str(cwd or self.tmp), env=self.env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True, check=True).stdout

    def run(self, script, *args):
        return subprocess.run([str(self.harness / "bin" / script)] + list(args), cwd=str(self.tmp),
                              env=self.env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              universal_newlines=True)

    def run_with_archify_archive(self, archive, digest, *args):
        # Pin the fixture copy so setup and its doctor subprocess use the same digest.
        module = self.harness / "lib/archify.py"
        source = module.read_text(encoding="utf-8")
        source, replaced = re.subn(r'^SHA256 = "[0-9a-f]{64}"$', f'SHA256 = "{digest}"', source, flags=re.M)
        assert replaced == 1
        module.write_text(source, encoding="utf-8")
        runner = """
from pathlib import Path
from unittest.mock import patch
import io
import runpy
import sys

setup, archive, *args = sys.argv[1:]
sys.path.insert(0, str(Path(setup).parent.parent / "lib"))
import archify

sys.argv = [setup, *args]
with patch.object(archify.urllib.request, "urlopen", return_value=io.BytesIO(Path(archive).read_bytes())):
    runpy.run_path(setup, run_name="__main__")
"""
        return subprocess.run(
            [sys.executable, "-c", runner, str(self.harness / "bin/setup"), str(archive), *args],
            cwd=self.tmp, env=self.env, capture_output=True, text=True)

    def backups(self):
        folder = self.home / ".bell-harness/backups"
        return sorted(p.name for p in folder.iterdir()) if folder.is_dir() else []

    def claude_calls(self):
        log = self.tmp / "claude-args.log"
        if not log.exists():
            return []
        return [json.loads(line) for line in log.read_text(encoding="utf-8").splitlines()]


class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.fx = Fixture(self.tmpdir.name)

    def tearDown(self):
        self.tmpdir.cleanup()

    def assert_installed(self):
        fx, home, harness = self.fx, self.fx.home, self.fx.harness
        for name in fx.skill_names:
            for folder in (".claude/skills", ".agents/skills"):
                self.assertEqual(os.readlink(str(home / folder / name)), str(harness / "skills" / name))
        self.assertEqual(os.readlink(str(home / ".codex/AGENTS.md")), str(harness / "global/AGENTS.md"))
        self.assertEqual(os.readlink(str(home / ".codex/rules/bell-harness.rules")),
                         str(harness / "config/bell-harness.rules"))
        claude_md = home / ".claude/CLAUDE.md"
        self.assertFalse(claude_md.is_symlink())
        self.assertEqual(claude_md.read_text(encoding="utf-8"), "@{}/global/CLAUDE.md\n".format(harness))
        self.assertEqual(fx.git("config", "--global", "core.hooksPath").strip(), str(harness / "git/hooks"))

    def test_install_then_noop(self):
        fx = self.fx
        result = fx.run("setup")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn(str(fx.home), result.stdout)
        self.assertNotIn(os.path.realpath(str(fx.home)), result.stdout)
        self.assertIn("setup: done (", result.stdout)
        after_done = result.stdout.split("setup: done (", 1)[1]
        self.assertIn("PASS link:", after_done)
        self.assert_installed()

        backup = fx.home / ".bell-harness/backups" / fx.backups()[0] / "home"
        for item in RETIRE["paths"]:
            self.assertTrue(os.path.lexists(str(backup / item)), item)
            self.assertFalse(os.path.lexists(str(fx.home / item)), item)
        self.assertEqual((backup / ".claude/skills/spec/SKILL.md").read_text(encoding="utf-8"), "old spec\n")
        self.assertTrue((backup / ".agents/skills/probe").is_symlink())

        self.assertIn(["plugin", "uninstall", "taste-skill@taste-skill"], fx.claude_calls())
        settings = fx.settings()
        before = fx.settings_before
        self.assertEqual(settings["hooks"], before["hooks"])
        self.assertEqual(settings["enabledPlugins"], {"codex@openai-codex": True})
        self.assertEqual(settings["theme"], "dark")
        self.assertEqual(settings["permissions"]["deny"][0], "Bash(rm -rf:*)")
        for rule in FRAGMENT["permissions"]["deny"]:
            self.assertIn(rule, settings["permissions"]["deny"])
        self.assertEqual(settings["attribution"], FRAGMENT["attribution"])
        mode = (fx.home / ".claude/settings.json").stat().st_mode & 0o777
        self.assertEqual(mode, 0o600)

        self.assertEqual((fx.home / ".claude/skills/paseo-x/SKILL.md").read_text(encoding="utf-8"), "paseo\n")
        self.assertEqual((fx.home / ".agents/skills/synced/SKILL.md").read_text(encoding="utf-8"), "synced\n")

        again = fx.run("setup")
        self.assertEqual(again.returncode, 0, again.stdout)
        self.assertIn("setup: nothing to do", again.stdout)
        self.assertEqual(len(fx.backups()), 1)

    def test_dry_run_changes_nothing(self):
        fx = self.fx
        before = tree_snapshot(fx.home)
        result = fx.run("setup", "--dry-run")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("would link ~/.claude/skills/spec", result.stdout)
        self.assertEqual(tree_snapshot(fx.home), before)
        self.assertEqual(fx.settings(), fx.settings_before)
        self.assertEqual(fx.backups(), [])
        self.assertEqual(fx.claude_calls(), [])

    def test_archify_setup_reuses_cache_and_restores_previous_skill(self):
        fx = self.fx
        archive = fx.tmp / "archify.zip"
        with zipfile.ZipFile(archive, "w") as package:
            package.writestr("archify/SKILL.md", "---\nname: archify\n---\n")
            package.writestr("archify/bin/archify.mjs", "console.log('archify');\n")
        digest = hashlib.sha256(archive.read_bytes()).hexdigest()
        existing = fx.home / ".agents/skills/archify"
        existing.mkdir()
        (existing / "SKILL.md").write_text("previous skill", encoding="utf-8")

        before = tree_snapshot(fx.home)
        preview = fx.run("setup", "--with-archify", "--dry-run")
        self.assertEqual(preview.returncode, 0, preview.stdout)
        self.assertIn("would download and verify Archify", preview.stdout)
        self.assertEqual(tree_snapshot(fx.home), before)
        self.assertFalse((fx.harness / ".harness-tools").exists())
        self.assertEqual(fx.backups(), [])

        result = fx.run_with_archify_archive(archive, digest, "--with-archify")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("setup: cached Archify", result.stdout)
        for directory in (".agents/skills", ".claude/skills"):
            skill = fx.home / directory / "archify"
            self.assertTrue(skill.is_symlink())
            self.assertIn(".harness-tools", skill.resolve().parts)
            self.assertEqual((skill / "bin/archify.mjs").read_text(encoding="utf-8"),
                             "console.log('archify');\n")
        cache = existing.resolve()

        archive.write_bytes(b"unexpected response")
        again = fx.run_with_archify_archive(archive, digest, "--with-archify")
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertIn("setup: nothing to do", again.stdout)
        self.assertEqual(len(fx.backups()), 1)

        restore = fx.run("setup", "--restore", fx.backups()[0])
        self.assertEqual(restore.returncode, 0, restore.stdout)
        self.assertEqual((existing / "SKILL.md").read_text(encoding="utf-8"), "previous skill")
        self.assertFalse((fx.home / ".claude/skills/archify").exists())
        self.assertTrue(cache.is_dir())

    def test_archify_setup_rejects_unverified_archive(self):
        fx = self.fx
        archive = fx.tmp / "invalid.zip"
        archive.write_bytes(b"unexpected response")
        before = tree_snapshot(fx.home)
        result = fx.run_with_archify_archive(archive, "0" * 64, "--with-archify")
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("does not match the pinned SHA-256", result.stdout)
        self.assertEqual(tree_snapshot(fx.home), before)
        self.assertEqual(fx.backups(), [])
        self.assertFalse((fx.harness / ".harness-tools").exists())

    def test_archify_setup_rejects_linked_cache(self):
        fx = self.fx
        outside = fx.tmp / "cache-target"
        outside.mkdir()
        (fx.harness / ".harness-tools").symlink_to(outside, target_is_directory=True)
        before = tree_snapshot(fx.home)
        result = fx.run("setup", "--with-archify")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("Archify cache is a symlink", result.stdout)
        self.assertEqual(list(outside.iterdir()), [])
        self.assertEqual(tree_snapshot(fx.home), before)
        self.assertEqual(fx.backups(), [])

    def test_removed_skill_loses_its_links(self):
        fx = self.fx
        self.assertEqual(fx.run("setup").returncode, 0)
        shutil.rmtree(str(fx.harness / "skills/probe"))
        result = fx.run("setup")
        self.assertIn("unlink ~/.claude/skills/probe", result.stdout)
        self.assertFalse(os.path.lexists(str(fx.home / ".claude/skills/probe")))
        self.assertFalse(os.path.lexists(str(fx.home / ".agents/skills/probe")))
        self.assertTrue((fx.home / ".claude/skills/spec").is_symlink())

    def test_restore_returns_the_previous_state(self):
        fx = self.fx
        before = tree_snapshot(fx.home)
        self.assertEqual(fx.run("setup").returncode, 0)
        backup_id = fx.backups()[0]
        settings = fx.settings()
        settings["attribution"]["commit"] = "custom"
        fx.write_settings(settings)

        result = fx.run("setup", "--restore", backup_id)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("restore: skipped ~/.claude/settings.json attribution (changed since setup)", result.stdout)
        self.assertIn("claude plugin install taste-skill@taste-skill", result.stdout)
        self.assertEqual(tree_snapshot(fx.home), before)
        hooks = subprocess.run(["git", "config", "--global", "--get", "core.hooksPath"], env=fx.env,
                               stdout=subprocess.PIPE, universal_newlines=True)
        self.assertEqual((hooks.returncode, hooks.stdout), (1, ""))
        restored = fx.settings()
        self.assertEqual(restored.pop("attribution")["commit"], "custom")
        expected = dict(fx.settings_before, enabledPlugins={"codex@openai-codex": True})
        self.assertEqual(restored, expected)
        self.assertEqual(fx.backups(), [backup_id + ".restored"])

    def test_preflight_failures_change_nothing(self):
        fx = self.fx
        before = tree_snapshot(fx.home)
        (fx.home / ".claude/settings.json").write_text("{not json", encoding="utf-8")
        result = fx.run("setup")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("setup: ", result.stdout)
        self.assertEqual(tree_snapshot(fx.home), before)
        self.assertFalse((fx.home / ".bell-harness").exists())

        fx.write_settings(fx.settings_before)
        fx.git("config", "--global", "core.hooksPath", str(fx.tmp / "other-hooks"))
        result = fx.run("setup")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("core.hooksPath", result.stdout)
        self.assertEqual(tree_snapshot(fx.home), before)
        self.assertFalse((fx.home / ".bell-harness").exists())


    def test_restore_rejects_bad_ids_and_damaged_manifests(self):
        fx = self.fx
        self.assertEqual(fx.run("setup").returncode, 0)
        result = fx.run("setup", "--restore", "../elsewhere")
        self.assertEqual(result.returncode, 2, result.stdout)
        installed = tree_snapshot(fx.home)
        backup_id = fx.backups()[0]
        manifest = fx.home / ".bell-harness/backups" / backup_id / "manifest.jsonl"
        with manifest.open("a", encoding="utf-8") as stream:
            stream.write('{"action": "retire", "path": "../../outside"}\n')
        result = fx.run("setup", "--restore", backup_id)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("is damaged", result.stdout)
        self.assertEqual(tree_snapshot(fx.home), installed)
        self.assertEqual(fx.backups(), [backup_id])

    def assert_damaged_manifest_leaves_install_unchanged(self, action, field):
        fx = self.fx
        self.assertEqual(fx.run("setup").returncode, 0)
        backup_id = fx.backups()[0]
        manifest = fx.home / ".bell-harness/backups" / backup_id / "manifest.jsonl"
        entries = [json.loads(line) for line in manifest.read_text().splitlines()]
        damaged = next(entry for entry in entries if entry["action"] == action)
        if action == "settings":
            damaged = damaged["previous"][0]
        del damaged[field]
        manifest.write_text("".join(json.dumps(entry) + "\n" for entry in entries))

        installed = tree_snapshot(fx.home)
        settings = (fx.home / ".claude/settings.json").read_bytes()
        hooks = Path(fx.env["GIT_CONFIG_GLOBAL"]).read_bytes()
        result = fx.run("setup", "--restore", backup_id)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("nothing was undone", result.stdout)
        self.assertEqual(tree_snapshot(fx.home), installed)
        self.assertEqual((fx.home / ".claude/settings.json").read_bytes(), settings)
        self.assertEqual(Path(fx.env["GIT_CONFIG_GLOBAL"]).read_bytes(), hooks)
        self.assertEqual(fx.backups(), [backup_id])

    def test_restore_rejects_an_incomplete_link_record(self):
        self.assert_damaged_manifest_leaves_install_unchanged("link", "target")

    def test_restore_rejects_an_incomplete_settings_record(self):
        self.assert_damaged_manifest_leaves_install_unchanged("settings", "key")

    def test_restore_survives_invalid_settings(self):
        fx = self.fx
        self.assertEqual(fx.run("setup").returncode, 0)
        (fx.home / ".claude/settings.json").write_text("{bad", encoding="utf-8")
        result = fx.run("setup", "--restore", fx.backups()[0])
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("Traceback", result.stdout)
        self.assertIn("restore: skipped ~/.claude/settings.json (not valid JSON", result.stdout)
        self.assertEqual((fx.home / ".claude/skills/spec/SKILL.md").read_text(encoding="utf-8"), "old spec\n")

    def test_failed_action_stops_and_can_be_undone(self):
        fx = self.fx
        before = tree_snapshot(fx.home)
        write_stub(fx.tmp, "claude", "#!/bin/sh\necho 'network error' >&2\nexit 1\n")
        result = fx.run("setup")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("setup: stopped after ", result.stdout)
        self.assertNotIn("link ~/.claude/skills/spec", result.stdout)  # not reached, so not printed
        self.assertEqual(fx.run("setup", "--restore", fx.backups()[0]).returncode, 0)
        self.assertEqual(tree_snapshot(fx.home), before)

    def test_restore_resumes_after_a_partial_undo(self):
        fx = self.fx
        self.assertEqual(fx.run("setup").returncode, 0)
        os.unlink(str(fx.home / ".claude/skills/spec"))
        result = fx.run("setup", "--restore", fx.backups()[0])
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("(resumed)", result.stdout)
        self.assertEqual((fx.home / ".claude/skills/spec/SKILL.md").read_text(encoding="utf-8"), "old spec\n")

    def test_settings_compare_json_types(self):
        fx = self.fx
        settings = dict(fx.settings_before, attribution={"commit": "", "pr": "", "sessionUrl": 0})
        fx.write_settings(settings)
        result = fx.run("setup", "--dry-run")
        self.assertIn("set attribution.sessionUrl false", result.stdout)

    def test_unsafe_layouts_are_refused_or_ignored(self):
        fx = self.fx
        local = fx.home / ".bell-harness/retire.local.json"
        local.parent.mkdir(parents=True)
        local.write_text(json.dumps({"paths": [".claude/skills", ".codex/skills/chronicle/SKILL.md"]}),
                         encoding="utf-8")
        demo = fx.harness / "skills/paseo-demo"
        demo.mkdir()
        (demo / "SKILL.md").write_text("---\nname: paseo-demo\n---\n", encoding="utf-8")
        result = fx.run("setup")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertNotIn("retire ~/.claude/skills (", result.stdout)
        self.assertNotIn("paseo-demo", result.stdout)
        self.assertEqual((fx.home / ".claude/skills/paseo-x/SKILL.md").read_text(encoding="utf-8"), "paseo\n")

        other = Fixture(str(fx.tmp / "second"))
        real = other.home / ".agents/skills"
        moved = other.tmp / "shared-skills"
        os.rename(str(real), str(moved))
        os.symlink(str(moved), str(real))
        result = other.run("setup")
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("is a symlink", result.stdout)

    def test_retirement_skips_symlinked_parent_but_moves_a_leaf_link(self):
        fx = self.fx
        outside = fx.tmp / "outside"
        outside.mkdir()
        external = outside / "record.txt"
        external.write_text("external\n", encoding="utf-8")
        linked_folder = fx.home / ".claude/commands/linked"
        linked_folder.symlink_to(outside)
        leaf = linked_folder.with_name("leaf")
        leaf.symlink_to(external)
        config = fx.home / ".bell-harness/retire.local.json"
        config.parent.mkdir(exist_ok=True)
        config.write_text(json.dumps({"paths": [
            ".claude/commands/linked/record.txt", ".claude/commands/leaf",
        ]}), encoding="utf-8")

        dry = fx.run("setup", "--dry-run")
        self.assertEqual(dry.returncode, 0, dry.stdout)
        self.assertIn("skipped ~/.claude/commands/linked/record.txt", dry.stdout)
        self.assertNotIn("would retire ~/.claude/commands/linked/record.txt", dry.stdout)
        installed = fx.run("setup")
        self.assertEqual(installed.returncode, 0, installed.stdout)
        self.assertIn("skipped ~/.claude/commands/linked/record.txt", installed.stdout)
        self.assertIn("WARN retired: ~/.claude/commands/linked/record.txt", installed.stdout)
        self.assertEqual(external.read_text(encoding="utf-8"), "external\n")
        self.assertFalse(leaf.is_symlink())

        restored = fx.run("setup", "--restore", fx.backups()[0])
        self.assertEqual(restored.returncode, 0, restored.stdout)
        self.assertEqual(leaf.readlink(), external)

    def test_restore_keeps_backup_when_retirement_parent_is_now_a_symlink(self):
        fx = self.fx
        self.assertEqual(fx.run("setup").returncode, 0)
        backup = fx.backups()[0]
        commands = fx.home / ".claude/commands"
        commands.rmdir()
        outside = fx.tmp / "outside"
        outside.mkdir()
        commands.symlink_to(outside)
        settings = (fx.home / ".claude/settings.json").read_bytes()
        git_config = Path(fx.env["GIT_CONFIG_GLOBAL"]).read_bytes()

        for args in (("--dry-run",), ()):
            result = fx.run("setup", "--restore", backup, *args)
            self.assertEqual(result.returncode, 2, result.stdout)
            self.assertIn("symlinked parent", result.stdout)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertEqual(fx.backups(), [backup])
            self.assertEqual((fx.home / ".claude/settings.json").read_bytes(), settings)
            self.assertEqual(Path(fx.env["GIT_CONFIG_GLOBAL"]).read_bytes(), git_config)

        commands.unlink()
        saved = fx.home / ".bell-harness/backups" / backup / "home/.claude/commands"
        moved = saved.rename(fx.tmp / "saved-commands")
        saved.symlink_to(moved)
        result = fx.run("setup", "--restore", backup)
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("symlinked parent", result.stdout)
        self.assertTrue((moved / "pre-push-check.md").is_file())
        self.assertEqual(fx.backups(), [backup])
        saved.unlink()
        moved.rename(saved)
        self.assertEqual(fx.run("setup", "--restore", backup).returncode, 0)
        self.assertTrue((commands / "pre-push-check.md").is_file())

    def test_setup_and_restore_reject_a_linked_backup_directory(self):
        fx = self.fx
        outside = fx.tmp / "outside-backups"
        outside.mkdir()
        backups = fx.home / ".bell-harness/backups"
        backups.parent.mkdir(exist_ok=True)
        backups.symlink_to(outside)
        before = tree_snapshot(fx.home)

        for args in (("--dry-run",), (), ("--restore", "all"), ("--list-backups",)):
            with self.subTest(args=args):
                result = fx.run("setup", *args)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertIn("backup directory", result.stdout)
                self.assertIn("symlink", result.stdout)
                self.assertEqual(list(outside.iterdir()), [])
                self.assertEqual(tree_snapshot(fx.home), before)

    def test_retirement_deduplicates_equivalent_paths(self):
        fx = self.fx
        item = ".claude/commands/pre-push-check.md"
        config = fx.home / ".bell-harness/retire.local.json"
        config.parent.mkdir(exist_ok=True)
        config.write_text(json.dumps({"paths": [
            ".claude/commands/./pre-push-check.md", item,
        ]}), encoding="utf-8")

        dry = fx.run("setup", "--dry-run")
        self.assertEqual(dry.returncode, 0, dry.stdout)
        self.assertEqual(dry.stdout.count("would retire ~/" + item + " ("), 1)
        installed = fx.run("setup")
        self.assertEqual(installed.returncode, 0, installed.stdout)
        self.assertFalse((fx.home / item).exists())
        backup = fx.home / ".bell-harness/backups" / fx.backups()[0]
        self.assertTrue((backup / "home" / item).is_file())

    def test_list_backups_reports_state_in_numeric_order_without_changes(self):
        fx = self.fx
        root = fx.home / ".bell-harness/backups"
        names = ("20261122T010101Z-2.restored", "20261122T010101Z-10", "20261121T010101Z")
        payload = json.dumps({"action": "uninstall-plugin", "path": "fixture-private-marker"}) + "\n"
        files = []
        for name in (*names, "unrecognized"):
            manifest = root / name / "manifest.jsonl"
            manifest.parent.mkdir(parents=True, exist_ok=True)
            manifest.write_text(payload, encoding="utf-8")
            files.append(manifest)
        before = (tree_snapshot(fx.home), fx.settings(), fx.backups(),
                  [path.read_bytes() for path in files], Path(fx.env["GIT_CONFIG_GLOBAL"]).read_bytes())

        result = fx.run("setup", "--list-backups")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(result.stdout.splitlines(), [
            "20261122T010101Z-10 active valid",
            "20261122T010101Z-2 restored valid",
            "20261121T010101Z active valid",
        ])
        after = (tree_snapshot(fx.home), fx.settings(), fx.backups(),
                 [path.read_bytes() for path in files], Path(fx.env["GIT_CONFIG_GLOBAL"]).read_bytes())
        self.assertEqual(after, before)
        self.assertEqual(fx.claude_calls(), [])

    def test_list_backups_accepts_empty_inventory_and_is_exclusive(self):
        fx = self.fx
        result = fx.run("setup", "--list-backups")
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("no backups found", result.stdout)
        for other in (("--dry-run",), ("--restore", "all")):
            with self.subTest(other=other):
                result = fx.run("setup", "--list-backups", *other)
                self.assertEqual(result.returncode, 2, result.stdout)

    def test_backup_reads_reject_linked_and_damaged_manifests(self):
        fx = self.fx
        root = fx.home / ".bell-harness/backups"
        outside = fx.tmp / "outside-backup"
        outside.mkdir()
        external = outside / "manifest.jsonl"
        payload = b'{"action":"uninstall-plugin","path":"fixture-private-marker"}\n'
        external.write_bytes(payload)

        root.mkdir(parents=True)
        linked_id = root / "20261122T010104Z"
        linked_id.symlink_to(outside, target_is_directory=True)
        linked_manifest = root / "20261122T010103Z"
        linked_manifest.mkdir()
        (linked_manifest / "manifest.jsonl").symlink_to(external)
        invalid_bytes = root / "20261122T010102Z"
        invalid_bytes.mkdir()
        (invalid_bytes / "manifest.jsonl").write_bytes(b"\xff\n")
        malformed = root / "20261122T010101Z.restored"
        malformed.mkdir()
        (malformed / "manifest.jsonl").write_text("fixture-private-marker\n", encoding="utf-8")

        result = fx.run("setup", "--list-backups")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertEqual(result.stdout.splitlines(), [
            "20261122T010104Z active unsafe",
            "20261122T010103Z active unsafe",
            "20261122T010102Z active damaged",
            "20261122T010101Z restored damaged",
        ])
        for backup in (linked_id, linked_manifest, invalid_bytes):
            with self.subTest(backup=backup.name):
                result = fx.run("setup", "--restore", backup.name, "--dry-run")
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertNotIn("Traceback", result.stdout)
                self.assertNotIn("fixture-private-marker", result.stdout)
        self.assertEqual(external.read_bytes(), payload)
        self.assertTrue(linked_id.is_symlink())
        self.assertTrue((linked_manifest / "manifest.jsonl").is_symlink())

    def test_restore_all_orders_numbered_backups(self):
        loader = importlib.machinery.SourceFileLoader("harness_setup", str(ROOT / "bin/setup"))
        spec = importlib.util.spec_from_loader("harness_setup", loader)
        module = importlib.util.module_from_spec(spec)
        loader.exec_module(module)
        names = ["20261120T010101Z", "20261120T010101Z-2", "20261120T010101Z-10", "20261121T000000Z"]
        ordered = sorted(names, key=module.backup_order, reverse=True)
        self.assertEqual(ordered, ["20261121T000000Z", "20261120T010101Z-10", "20261120T010101Z-2",
                                   "20261120T010101Z"])


if __name__ == "__main__":
    unittest.main()
