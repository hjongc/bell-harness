import unittest

from harness_env import ROOT


class InstructionTests(unittest.TestCase):
    def test_instruction_lengths_and_wording(self):
        for path, limit in (
            ("global/AGENTS.md", 70),
            ("global/CLAUDE.md", 30),
            ("templates/AGENTS.md", 60),
            ("AGENTS.md", 60),
        ):
            with self.subTest(path=path):
                text = (ROOT / path).read_text(encoding="utf-8")
                self.assertLessEqual(len(text.splitlines()), limit)
                self.assertNotRegex(text, r"\b(MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT)\b")
                self.assertNotRegex(text, r"(?i)if in doubt")

    def test_claude_imports_shared_instructions(self):
        lines = (ROOT / "global/CLAUDE.md").read_text(encoding="utf-8").splitlines()
        self.assertEqual(lines[0], "@AGENTS.md")

    def test_shared_instructions_offer_question_choices(self):
        text = (ROOT / "global/AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("question widget", text)
        self.assertIn("numbered fallback", text)
        self.assertIn("what each option leads to", text)

    def test_project_template_headings(self):
        lines = (ROOT / "templates/AGENTS.md").read_text(encoding="utf-8").splitlines()
        for heading in (
            "Non-goals", "Decision priorities", "Sources of truth", "Commands", "Skills",
            "Permission boundaries", "Commit rules", "Evals",
        ):
            with self.subTest(heading=heading):
                self.assertIn(f"## {heading}", lines)
