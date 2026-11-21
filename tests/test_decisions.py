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

    def test_accepts_a_record_wrapped_onto_indented_lines(self):
        text = "## Decisions\n- D1: Keep it -- why: a long\n  reason -- by: observed\n  -- paths: lib\n\n- D2: Next -- why: r -- by: user\n"
        decisions, errors = parse(text, "spec")
        self.assertEqual(errors, [])
        self.assertEqual([(d.ref, d.why, d.by, d.paths) for d in decisions],
                         [("spec#D1", "a long reason", "observed", ["lib"]), ("spec#D2", "r", "user", [])])

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

    def test_self_supersession_is_reported(self):
        documents = {"a.md": "## Decisions\n" + VALID + " -- paths: gone.txt -- supersedes: a#D1\n"}
        problems = self.check_fixture(documents)
        self.assertIn("docs/plans/a.md:2: a#D1 supersedes itself", problems)
        self.assertIn("docs/plans/a.md:2: a#D1 cites missing path gone.txt", problems)

    def test_sources_table_tracks_current_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_plans(root, {"a.md": "## Decisions\n" + VALID
                               + "\n- D2: Second -- why: changed -- by: user -- supersedes: a#D1"
                               + "\n- D3: Third -- why: changed -- by: user -- supersedes: a#D2\n"})
            agents = root / "AGENTS.md"
            table = "## Sources of truth\n| Task | `example` | {} |\n## Commands\n| x | x | gone#D9 |"
            agents.write_text(table.format("a#D1 and gone#D1"), encoding="utf-8")
            self.assertEqual(check(root), ["AGENTS.md:2: a#D1 superseded; cite a#D3",
                                           "AGENTS.md:2: unknown decision gone#D1"])
            agents.write_text(table.format("a#D3 replaces a#D1"), encoding="utf-8")
            self.assertEqual(check(root), [])
            with (root / "docs/plans/a.md").open("a") as extra:
                extra.write("- D4: Fourth -- why: changed -- by: user -- supersedes: a#D3\n")
            path = root / "docs/plans/a.md"
            path.write_text(path.read_text().replace(VALID, VALID + " -- supersedes: a#D4"))
            self.assertIn("AGENTS.md:2: a#D1 has no active successor", check(root))

    def test_repository_records_are_valid(self):
        self.assertEqual(check(ROOT), [])

    def test_roadmap_items_reference_existing_specs(self):
        documents = {
            "roadmap.md": "# Roadmap\n\n- [x] existing: done\n- [ ] missing: next\n- [x] also-missing: done\n",
            "existing.md": "Status: implemented\n",
        }
        self.assertEqual(self.check_fixture(documents), [
            "docs/plans/roadmap.md:4: unknown spec missing",
            "docs/plans/roadmap.md:5: unknown spec also-missing",
        ])


if __name__ == "__main__":
    unittest.main()
