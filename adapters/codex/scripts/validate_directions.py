#!/usr/bin/env python3
import sys
from pathlib import Path

from directions_state import load_state, state_path, validate_state


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    path = state_path(repo_root)
    if not path.exists():
        try:
            load_state(repo_root)
        except FileNotFoundError:
            print(f"Missing {path}")
            return 1

    errors = validate_state(load_state(repo_root))
    if errors:
        for error in errors:
            print(error)
        return 1

    print(f"OK {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
