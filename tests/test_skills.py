import re
import unittest

from harness_env import ROOT


SKILLS = ROOT / "skills"
EXPECTED = {
    "away", "business-document-design", "eval", "map", "offline-verification", "preflight", "probe",
    "repo-diagrams", "spec", "systematic-debugging", "ui-design", "ui-polish",
}
EMPHASIS = re.compile(r"\b(MUST|NEVER|ALWAYS|CRITICAL|IMPORTANT)\b")
LOCAL_REF = re.compile(r"(?<![\w/<-])((?:references|scripts)/[\w.-]+\.(?:md|py|mjs))")


def frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return None
    fields = {}
    for line in lines[1:]:
        if line == "---":
            return fields
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip('"')
    return None


class SkillTests(unittest.TestCase):
    def test_expected_skills_exist(self):
        names = {p.name for p in SKILLS.iterdir() if (p / "SKILL.md").is_file()}
        self.assertEqual(names, EXPECTED)

    def test_skill_files_follow_the_format(self):
        for name in sorted(EXPECTED):
            path = SKILLS / name / "SKILL.md"
            text = path.read_text(encoding="utf-8")
            with self.subTest(skill=name):
                fields = frontmatter(text)
                self.assertIsNotNone(fields, "missing frontmatter")
                self.assertEqual(fields.get("name"), name)
                description = fields.get("description", "")
                raw = [l for l in text.splitlines() if l.startswith("description:")][0]
                if not raw[len("description:"):].strip().startswith('"'):
                    self.assertNotIn(": ", description, "quote a description that contains ': ' (YAML)")
                self.assertTrue(0 < len(description) <= 1024, len(description))
                self.assertIn("Use ", description)
                self.assertLessEqual(len(text.splitlines()), 250)
                self.assertNotRegex(text, EMPHASIS)
                for ref in LOCAL_REF.findall(text):
                    self.assertTrue((SKILLS / name / ref).exists(), ref)

    def test_requirements_template_fields_and_statuses(self):
        text = (ROOT / "templates/requirements.md").read_text(encoding="utf-8")
        self.assertIn("| ID | Requirement | Acceptance criteria | Status | Spec |", text.splitlines())
        for status in ("todo", "in-progress", "done", "dropped"):
            with self.subTest(status=status):
                self.assertIn(f"`{status}`", text)

    def test_away_skill_references_run_procedure(self):
        text = (SKILLS / "away/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("references/run.md", text)

    def test_third_party_skills_have_licenses(self):
        self.assertTrue((ROOT / "licenses/ui-ux-pro-max.txt").is_file())
        self.assertTrue((ROOT / "licenses/gstack.txt").is_file())
        sources = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
        for name in EXPECTED:
            self.assertIn("skills/" + name, sources)


if __name__ == "__main__":
    unittest.main()
