import re
import subprocess
import tempfile
import unittest
from pathlib import Path

from harness_env import ROOT, init_repo, make_env


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

    def test_away_folder_check_detects_changes(self):
        text = (SKILLS / "away/references/run.md").read_text(encoding="utf-8")
        script = text.split("## Separate folder", 1)[1].split("```sh\n", 1)[1].split("```", 1)[0]
        with tempfile.TemporaryDirectory() as tmp:
            env, repo, folder = make_env(Path(tmp)), Path(tmp) / "repo", Path(tmp) / "item"
            init_repo(repo, env)

            def run(*command, cwd=repo):
                return subprocess.check_output(command, cwd=cwd, env=env, text=True)

            (repo / "a").write_text("one\n")
            run("git", "add", "a")
            run("git", "commit", "-q", "-m", "chore: start")
            (repo / "a").write_text("draft\n")
            (repo / "new").mkdir()
            (repo / "new/초안").write_text("draft\n")
            before = run("sh", "-c", script)
            run("git", "worktree", "add", "-q", str(folder), "-b", "feat/x", "main")
            (folder / "b").write_text("two\n")
            run("git", "add", "b", cwd=folder)
            run("git", "commit", "-q", "-m", "feat: add b", cwd=folder)
            run("git", "worktree", "remove", str(folder))
            self.assertEqual(run("sh", "-c", script), before)
            for path in ("a", "new/초안"):
                (repo / path).write_text("changed\n")
                self.assertNotEqual(run("sh", "-c", script), before, path)
                (repo / path).write_text("draft\n")

    def test_third_party_skills_have_licenses(self):
        self.assertTrue((ROOT / "licenses/ui-ux-pro-max.txt").is_file())
        self.assertTrue((ROOT / "licenses/gstack.txt").is_file())
        sources = (ROOT / "SOURCES.md").read_text(encoding="utf-8")
        for name in EXPECTED:
            self.assertIn("skills/" + name, sources)


if __name__ == "__main__":
    unittest.main()
