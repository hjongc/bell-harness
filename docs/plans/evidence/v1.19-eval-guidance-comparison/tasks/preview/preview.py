"""Render a title with a template beside the installed CLI."""

import argparse
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("title")
    title = parser.parse_args().title
    template_path = Path(__file__).with_name("preview.txt")
    try:
        template = template_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        template = "Preview: {title}\n"
    print(template.replace("{title}", title), end="")


if __name__ == "__main__":
    main()
