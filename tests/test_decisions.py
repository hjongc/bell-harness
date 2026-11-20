import sys
import tempfile
import unittest
from pathlib import Path

from harness_env import ROOT

sys.path.insert(0, str(ROOT / "lib"))
from decisions import check, parse


VALID = "- D1: Keep it -- why: reason -- by: user"


def write_plans(root, documents):
    plans = root / "docs/plans"
    plans.mkdir(parents=True)
    for name, body in documents.items():
        (plans / name).write_text(body, encoding="utf-8")


class ParseTests(unittest.TestCase):
    def test_parses_fields_inside_the_section_only(self):
        text = "\n".join([
            "## Context",
            "- D9: not a record here",
            "## Decisions",
            "- D1: Use A -- why: B -- by: observed -- paths: lib x -- supersedes: other#D2",
            "```",
            "- D<n>: template line",
            "```",
            "- Decisions are prose too",
            "## Next",
        ])
        decisions, errors = parse(text, "spec")
        self.assertEqual(errors, [])
        self.assertEqual(len(decisions), 1)
        decision = decisions[0]
        self.assertEqual((decision.ref, decision.text, decision.why, decision.by),
                         ("spec#D1", "Use A", "B", "observed"))
        self.assertEqual(decision.paths, ["lib", "x"])
        self.assertEqual(decision.supersedes, ["other#D2"])

    def test_rejects_malformed_lines(self):
        for line in (
            "- D1: Keep it -- by: user",
            "- D1: Keep it -- why: reason -- by: maybe",
            "- D1: Keep it -- by: user -- why: reason",
            "- D1: Keep it -- why: reason -- by: user -- note: extra",
            "- D1: Keep it -- why: reason -- by: user -- supersedes: D3",
            "- D1 Keep it -- why: reason -- by: user",
        ):
            with self.subTest(line=line):
                decisions, errors = parse("## Decisions\n" + line, "spec")
                self.assertEqual(decisions, [])
                self.assertEqual(len(errors), 1)


class CheckTests(unittest.TestCase):
    def check_fixture(self, documents, files=()):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_plans(root, documents)
            for name in files:
                (root / name).write_text("", encoding="utf-8")
            return check(root)

    def test_valid_records_have_no_problems(self):
        documents = {
            "a.md": "## Decisions\n" + VALID + " -- paths: kept.txt\n",
            "b.md": "## Decisions\n- D1: New -- why: r -- by: user -- supersedes: a#D1\n",
        }
        self.assertEqual(self.check_fixture(documents, ["kept.txt"]), [])

    def test_each_problem_is_reported_once(self):
        documents = {
            "a.md": "\n".join([
                "## Decisions",
                "- D1: x -- why: r",
                VALID,
                VALID,
                "- D2: y -- why: r -- by: user -- supersedes: gone#D4",
                "- D3: z -- why: r -- by: user -- paths: missing.txt",
            ]),
        }
        problems = self.check_fixture(documents)
        self.assertEqual(len(problems), 4, problems)
        self.assertIn("docs/plans/a.md:2: missing field 'by'", problems)
        self.assertIn("docs/plans/a.md:4: duplicate id D1", problems)
        self.assertIn("docs/plans/a.md:5: supersedes unknown decision gone#D4", problems)
        self.assertIn("docs/plans/a.md:6: a#D3 cites missing path missing.txt", problems)

    def test_superseded_decision_may_cite_a_removed_path(self):
        documents = {
            "a.md": "## Decisions\n" + VALID + " -- paths: removed.txt\n",
            "b.md": "## Decisions\n- D1: New -- why: r -- by: user -- supersedes: a#D1\n",
        }
        self.assertEqual(self.check_fixture(documents), [])

    def test_repository_records_are_valid(self):
        self.assertEqual(check(ROOT), [])


if __name__ == "__main__":
    unittest.main()
