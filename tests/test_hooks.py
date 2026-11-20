import json
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

from harness_env import HOOKS, init_repo, make_env, write_stub


CHAIN_HOOKS = (
    "applypatch-msg", "pre-applypatch", "post-applypatch", "pre-merge-commit",
    "prepare-commit-msg", "post-commit", "pre-rebase", "post-checkout", "post-merge",
    "pre-push", "pre-receive", "update", "proc-receive", "post-receive", "post-update",
    "reference-transaction", "push-to-checkout", "pre-auto-gc", "post-rewrite",
    "sendemail-validate", "fsmonitor-watchman", "p4-changelist", "p4-prepare-changelist",
    "p4-post-changelist", "p4-pre-submit", "post-index-change",
)


class HookTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name)
        self.repo = self.tmp / "repo"
        self.env = make_env(self.tmp)
        init_repo(self.repo, self.env)
        self.local_hooks = self.repo / ".git/hooks"

    def run_command(self, *command, cwd=None, env=None):
        return subprocess.run(
            command, cwd=cwd or self.repo, env=env or self.env, capture_output=True,
            encoding="utf-8", timeout=10,
        )

    def git(self, *args, **kwargs):
        return self.run_command("git", *args, **kwargs)

    def commit(self, message, **kwargs):
        return self.git("commit", "--allow-empty", "--cleanup=verbatim", "-m", message, **kwargs)

    def check_message(self, message):
        msgfile = self.tmp / "message"
        msgfile.write_text(message, encoding="utf-8")
        return self.run_command(HOOKS / "commit-msg", msgfile)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stderr)

    def assert_rejected(self, result, diagnostic):
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertTrue(result.stderr.startswith(diagnostic), result.stderr)

    def write_config(self, config):
        (self.repo / ".harness.json").write_text(json.dumps(config), encoding="utf-8")

    def marker_hook(self, name, body):
        hook = self.local_hooks / name
        write_stub(self.tmp, name, f"#!/bin/sh\n{body}\n").replace(hook)
        return self.local_hooks / f"{name}.marker"

    def test_accepts_default_and_exempt_subjects(self):
        for message in (
            "feat(visuals): cap demand posts at three images",
            "docs: add the lesson",
            "Merge branch 'x'",
            'Revert "feat: x"',
            'Reapply "feat: x"',
            "fixup! feat: x",
            "squash! feat: x",
            "amend! feat: x",
            "fix: " + "a" * 66 + "e\u0301",
        ):
            with self.subTest(message=message):
                self.assert_success(self.commit(message))

    def test_rejects_invalid_messages(self):
        for message, reason in (
            ("R90a: reader KPIs", "subject does not match the pattern"),
            ("Add deposits to the paper portfolio", "subject does not match the pattern"),
            ("fix: " + "a" * 68, "subject is too long"),
            ("fix: 버튼 수정", "message contains Hangul"),
            ("fix: adjust the layout\n\nCo-Authored-By: A <a@example.com>", "Co-Authored-By is not allowed"),
            ("", "empty message"),
        ):
            with self.subTest(message=message):
                result = self.commit(message)
                self.assert_rejected(result, f"commit-msg: {reason}\n")
                self.assertEqual(
                    result.stderr.splitlines()[1:],
                    [
                        "expected: type(scope): English imperative summary (<= 72 chars, no Co-Authored-By)",
                        "example: fix(editorial): keep median labels inside the chart",
                    ],
                )

    def test_hangul_setting_only_applies_from_head(self):
        message = "fix(ui): 버튼 정렬 수정"
        self.write_config({"commit": {"allow_hangul": True}})
        self.assert_rejected(self.check_message(message), "commit-msg: message contains Hangul\n")
        self.assert_success(self.git("add", ".harness.json"))
        self.assert_rejected(self.commit(message), "commit-msg: message contains Hangul\n")
        self.assert_success(self.commit("chore: allow Hangul in commit messages"))
        self.assert_success(self.commit(message))

    def test_uses_committed_subject_pattern_and_length(self):
        pattern = r"^ship: \S.*$"
        self.write_config({"commit": {"subject_pattern": pattern, "max_subject": 14}})
        self.assert_success(self.git("add", ".harness.json"))
        self.assert_success(self.commit("chore: configure commit subjects"))
        self.assert_success(self.commit("ship: ready"))
        for message, reason in (
            ("fix: wrong type", "subject does not match the pattern"),
            ("ship: " + "x" * 9, "subject is too long"),
        ):
            with self.subTest(message=message):
                result = self.commit(message)
                self.assert_rejected(result, f"commit-msg: {reason}\n")
                self.assertIn(f"expected: {pattern} (<= 14 chars, no Co-Authored-By)\n", result.stderr)

    def test_rejects_invalid_head_config(self):
        (self.repo / ".harness.json").write_text("{", encoding="utf-8")
        self.assert_success(self.git("add", ".harness.json"))
        self.assert_success(self.commit("test: add invalid fixture config"))
        self.assert_rejected(self.check_message("docs: add a note"), "commit-msg: invalid .harness.json\n")
        self.assert_rejected(self.run_command(HOOKS / "pre-commit"), "pre-commit: invalid .harness.json\n")

    def test_ignores_comments_and_text_below_scissors(self):
        for setting, comment in ((None, "#"), ("auto", "#"), (";", ";")):
            with self.subTest(setting=setting):
                if setting is not None:
                    self.assert_success(self.git("config", "core.commentChar", setting))
                message = (
                    f"{comment} 숨김\n\n"
                    "fix: keep the subject\n\n"
                    f"{comment} ------------------------ >8 ------------------------\n"
                    "+버튼 수정\n"
                )
                self.assert_success(self.check_message(message))

    def test_secret_allowlist_only_applies_from_head(self):
        value = "sk-" + "proj-" + "a" * 32
        name = "new notes.txt"
        (self.repo / name).write_text(f'header\nOPENAI_API_KEY="{value}"\n', encoding="utf-8")
        self.assert_success(self.commit("docs: initialize the test repository"))
        self.write_config({"secrets": {"allow": [re.escape(value)]}})
        self.assert_success(self.git("add", "--", name, ".harness.json"))
        result = self.commit("test: add a fixture")
        self.assert_rejected(result, "pre-commit:")
        self.assertIn(f"pre-commit: possible openai-key in {name}:2\n", result.stderr)
        self.assertNotIn(value, result.stdout + result.stderr)

        self.assert_success(self.git("restore", "--staged", "--", name))
        self.assert_success(self.commit("chore: allow the fixture key"))
        self.assert_success(self.git("add", "--", name))
        self.assert_success(self.commit("test: add an allowed fixture"))

    def test_scans_added_text_from_inherited_index(self):
        value = "sk-" + "proj-" + "a" * 32
        name = "patch\tlabel.txt"
        path = self.repo / name
        path.write_text("first line\n", encoding="utf-8")
        (self.repo / "binary").write_bytes(b"\0" + value.encode())
        self.assert_success(self.git("add", "--", name, "binary"))
        path.write_text(f"first line\n++ b/decoy\n{value}\n", encoding="utf-8")
        self.assert_success(self.commit("test: commit the staged text and binary file"))

        env = {**self.env, "GIT_INDEX_FILE": str(self.tmp / "alternate-index")}
        self.assert_success(self.git("read-tree", "HEAD", env=env))
        self.assert_success(self.git("add", "--", name, env=env))
        result = self.commit("test: inspect the alternate index", env=env)
        self.assert_rejected(result, f"pre-commit: possible openai-key in {name}:3\n")
        self.assertNotIn(value, result.stdout + result.stderr)

    def test_chains_repository_hooks_on_pass(self):
        before = self.marker_hook("pre-commit", 'touch "$0.marker"')
        prepare = self.marker_hook("prepare-commit-msg", 'printf "%s\n" "$2" > "$0.marker"')
        commit_msg = self.marker_hook("commit-msg", 'cat "$1" > "$0.marker"')
        after = self.marker_hook("post-commit", 'touch "$0.marker"')

        self.assert_rejected(self.commit("bad subject"), "commit-msg:")
        self.assertFalse(commit_msg.exists())
        self.assertFalse(after.exists())
        self.assertTrue(before.exists())
        self.assertEqual(prepare.read_text(encoding="utf-8"), "message\n")

        self.assert_success(self.commit("docs: add a note"))
        self.assertEqual(commit_msg.read_text(encoding="utf-8"), "docs: add a note\n")
        self.assertTrue(after.exists())

    def test_symlinks_back_to_harness_do_not_loop(self):
        for name, target in (
            ("commit-msg", "commit-msg"),
            ("pre-commit", "pre-commit"),
            ("post-commit", "_chain"),
        ):
            (self.local_hooks / name).symlink_to(HOOKS / target)
        self.assert_success(self.commit("docs: add a note"))

    def test_uses_common_hooks_in_linked_worktree(self):
        self.assert_success(self.commit("docs: initialize the test repository"))
        worktree = self.tmp / "linked"
        self.assert_success(self.git("worktree", "add", "-b", "linked", worktree))
        marker = self.marker_hook("post-commit", 'pwd > "$0.marker"')
        self.assert_rejected(self.commit("bad subject", cwd=worktree), "commit-msg:")
        self.assertFalse(marker.exists())
        self.assert_success(self.commit("docs: write from the worktree", cwd=worktree))
        self.assertEqual(Path(marker.read_text(encoding="utf-8").rstrip()).resolve(), worktree.resolve())


class HookFilesTests(unittest.TestCase):
    def test_hooks_are_executable_regular_files(self):
        chain = (HOOKS / "_chain").read_bytes()
        for name in ("_chain", "commit-msg", "pre-commit", *CHAIN_HOOKS):
            with self.subTest(name=name):
                hook = HOOKS / name
                mode = hook.lstat().st_mode
                self.assertTrue(stat.S_ISREG(mode))
                self.assertEqual(stat.S_IMODE(mode), 0o755)
                if name in CHAIN_HOOKS:
                    self.assertEqual(hook.read_bytes(), chain)
