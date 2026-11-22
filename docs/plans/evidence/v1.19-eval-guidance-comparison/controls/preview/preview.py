"""Render a title with a template beside the installed CLI."""

import argparse
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title")
    title = parser.parse_args().title
    template_path = Path(__file__).with_name("preview.txt")
    try:
        template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        print("missing installed template: preview.txt", file=sys.stderr)
        return 2
    print(template.replace("{title}", title), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
