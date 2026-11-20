import ast
import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from privacy import in_git_work_tree, repository_files


PYTHON3_SHEBANG = re.compile(
    rb"^\#![ \t]*(?:(?:\S*/)?env[ \t]+(?:-S[ \t]+)?)?(?:\S*/)?python3(?:\.[0-9]+)?(?=\s|$)"
)


class Python39Tests(unittest.TestCase):
    def test_python_sources_parse_with_python39_grammar(self):
        for path in repository_files(ROOT, in_git_work_tree(ROOT)):
            if not path.is_file():
                continue
            with path.open("rb") as stream:
                first_line = stream.readline()
                if path.suffix == ".py" or PYTHON3_SHEBANG.match(first_line):
                    name = path.relative_to(ROOT).as_posix()
                    with self.subTest(path=name):
                        ast.parse(first_line + stream.read(), filename=name, feature_version=(3, 9))
