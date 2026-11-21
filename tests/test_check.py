import runpy
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from harness_env import ROOT


snapshot_home = runpy.run_path(str(ROOT / "scripts/check"))["snapshot_home"]


class HomeGuardTests(unittest.TestCase):
    def test_detects_existing_backup_manifest_edits(self):
        key = ".bell-harness/backups"
        with tempfile.TemporaryDirectory() as directory, mock.patch(
            "subprocess.run", return_value=subprocess.CompletedProcess([], 1, stdout=b""),
        ):
            home = Path(directory)
            backups = home / key
            active = backups / "20261121T000000Z"
            restored = backups / "20261122T000000Z.restored"
            linked = backups / "20261123T000000Z"
            for backup in (active, restored, linked):
                backup.mkdir(parents=True)
            outside = home / "linked-manifest.jsonl"
            outside.write_text("one", encoding="utf-8")
            (linked / "manifest.jsonl").symlink_to(outside)
            for backup in (active, restored):
                (backup / "manifest.jsonl").write_text("one", encoding="utf-8")

            before = snapshot_home(home)
            outside.write_text("two", encoding="utf-8")
            self.assertEqual(snapshot_home(home), before)
            for backup in (active, restored):
                with self.subTest(backup=backup.name):
                    (backup / "manifest.jsonl").write_text("two", encoding="utf-8")
                    after = snapshot_home(home)
                    self.assertEqual([name for name in before if before[name] != after[name]], [key])
                    before = after
