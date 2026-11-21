import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path, PurePosixPath

from harness_env import ROOT, make_env


CONFIG = ROOT / "config"


class ConfigTests(unittest.TestCase):
    def test_claude_settings(self):
        self.assertEqual(
            json.loads((CONFIG / "claude-settings.json").read_text(encoding="utf-8")),
            {
                "attribution": {"commit": "", "pr": "", "sessionUrl": False},
                "permissions": {
                    "deny": [
                        "Bash(git commit --no-verify:*)",
                        "Bash(git commit -n:*)",
                        "Bash(git push --no-verify:*)",
                        "Bash(git * --no-verify*)",
                        "Bash(git -c core.hooksPath*)",
                        "Bash(git config*core.hooksPath*)",
                        "Bash(git commit * -n)",
                        "Bash(git commit * -n *)",
                        "Bash(git * commit -n*)",
                    ],
                },
            },
        )

    def test_codex_rules(self):
        self.assertEqual(
            (CONFIG / "bell-harness.rules").read_text(encoding="utf-8").splitlines(),
            [
                'prefix_rule(pattern=["git", "commit", "--no-verify"], decision="forbidden")',
                'prefix_rule(pattern=["git", "commit", "-n"], decision="forbidden")',
                'prefix_rule(pattern=["git", "push", "--no-verify"], decision="forbidden")',
            ],
        )

    def test_codex_execpolicy_forbids_no_verify(self):
        codex = shutil.which("codex")
        if not codex:
            self.skipTest("codex is not on PATH")
        with tempfile.TemporaryDirectory() as directory:
            env = make_env(Path(directory))
            # A Codex launcher may need an interpreter from the test process's PATH.
            env["PATH"] = os.environ.get("PATH", os.defpath)
            result = subprocess.run(
                [codex, "execpolicy", "check", "--rules", "config/bell-harness.rules",
                 "git", "commit", "--no-verify", "-m", "x"],
                cwd=ROOT, env=env, capture_output=True, text=True, timeout=10,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["decision"], "forbidden")

    def test_retired_items(self):
        retire = json.loads((CONFIG / "retire.json").read_text(encoding="utf-8"))
        self.assertEqual(
            retire,
            {
                "paths": [
                    ".claude/skills/interview",
                    ".claude/skills/morning-brief",
                    ".claude/commands/pre-push-check.md",
                    ".codex/skills/chronicle",
                    ".codex/skills/codex-goal-planner",
                    ".codex/skills/frontend-polish-review",
                    ".codex/skills/gpt-tasteskill",
                    ".codex/skills/imagegen-frontend-mobile",
                    ".codex/skills/redesign-skill",
                    ".codex/skills/soft-skill",
                    ".codex/skills/taste-skill",
                ],
                "claude_plugins": ["taste-skill@taste-skill"],
            },
        )
        for path in retire["paths"]:
            with self.subTest(path=path):
                self.assertFalse(PurePosixPath(path).is_absolute())
                self.assertTrue(path.startswith((".claude/", ".codex/")))
                self.assertNotIn("..", PurePosixPath(path).parts)
