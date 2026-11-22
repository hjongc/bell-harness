"""Build an installable preview directory."""

import argparse
import shutil
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("install_directory", type=Path)
    install_directory = parser.parse_args().install_directory
    install_directory.mkdir(parents=True)
    for filename in ("preview.py", "preview.txt"):
        shutil.copyfile(Path(__file__).with_name(filename), install_directory / filename)


if __name__ == "__main__":
    main()
