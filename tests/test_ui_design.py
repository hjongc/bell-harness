import subprocess
import tempfile
import unittest

from harness_env import ROOT


class UiDesignSearchTest(unittest.TestCase):
    def test_search_runs_and_prints_results(self):
        script = ROOT / "skills/ui-design/scripts/search.py"
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                ["/usr/bin/python3", str(script), "fintech dashboard"],
                cwd=tmp,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(result.stdout.strip())


if __name__ == "__main__":
    unittest.main()
