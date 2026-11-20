import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from privacy import scan


class PrivacyTests(unittest.TestCase):
    def run_fixture_scan(self, root):
        return subprocess.run(
            [sys.executable, str(ROOT / "lib/privacy.py"), str(root)],
            env={
                **os.environ,
                "GIT_CEILING_DIRECTORIES": str(root.parent.resolve()),
                "PYTHONDONTWRITEBYTECODE": "1",
            },
            capture_output=True,
            text=True,
        )

    def test_detects_kinds_without_printing_matches(self):
        assigned_value = "Ab1" * 4
        private_term = "fixture" + "-restricted-phrase"
        samples = [
            ("openai-key", "sk-" + "proj-" + "a1" * 16),
            ("anthropic-key", "sk-" + "ant-" + "b2" * 18),
            ("github-token", "gh" + "p_" + "c3" * 18),
            ("github-token", "github" + "_pat_" + "d4" * 10),
            ("aws-key", "AK" + "IA" + "E5" * 8),
            ("private-key", "-----BEGIN " + "PRIVATE KEY-----"),
            ("assigned-secret", f'OPENAI_API_KEY="{assigned_value}"'),
            ("home-path", "/Us" + "ers/fixture"),
            ("home-path", "/ho" + "me/fixture"),
            ("email", "fixture.user" + "@mail" + ".invalid"),
            ("private-term", private_term.upper()),
        ]
        allowed = [
            'token = "${TOKEN}"',
            'api_key = "<your-key>"',
            'token = "${LONG_TOKEN_123}"',
            'password = "{{LONG_TOKEN_123}}"',
            'api_key = "<your-long-key-123>"',
            "fixture" + "@users.noreply.github.com",
        ]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".private-terms").write_text(f"\n# ignored\n{private_term}\n", encoding="utf-8")
            lines = [value for _, value in samples] + allowed
            (root / "samples.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
            (root / "binary.data").write_bytes(b"\0" + samples[0][1].encode())
            result = self.run_fixture_scan(root)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stderr, "")
        self.assertEqual(
            result.stdout.splitlines(),
            [f"PRIVACY: samples.txt:{number}: {kind}" for number, (kind, _) in enumerate(samples, 1)],
        )

    def test_allow_rule_matches_path_and_kind(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "sample.txt").write_text("fixture" + "@mail" + ".invalid\n", encoding="utf-8")
            (root / ".privacy-allow").write_text("sample.* email\n", encoding="utf-8")
            result = self.run_fixture_scan(root)

        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "PRIVACY: clean\n")
        self.assertEqual(result.stderr, "")

    def test_repository_is_clean(self):
        self.assertEqual(scan(ROOT), [])
