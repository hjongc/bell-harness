"""Inert publication fixture. Print an argument receipt and do nothing else."""

import json
import sys


if __name__ == "__main__":
    print("bell-harness-fake-publish " + json.dumps(sys.argv[1:]))
    raise SystemExit(0 if sys.argv[1:] == ["fixture-package", "1.0.0"] else 2)
