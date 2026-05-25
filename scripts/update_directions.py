#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from directions_state import append_history, create_initial_state, mark_latest_event


def main():
    parser = argparse.ArgumentParser(description="Update repo-local Smallest Human Action state.")
    parser.add_argument("repo_root")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--project-name", required=True)
    init_parser.add_argument("--goal", required=True)
    init_parser.add_argument("--context", action="append", default=[])
    init_parser.add_argument("--directions-json", required=True, help="JSON array of direction objects")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("direction_id")
    show_parser.add_argument("--action", required=True)

    for command in ("in_progress", "done", "too_hard", "skip", "not_now"):
        event_parser = subparsers.add_parser(command)
        event_parser.add_argument("--result")

    args = parser.parse_args()
    repo_root = Path(args.repo_root)

    if args.command == "init":
        state = create_initial_state(
            repo_root,
            project_name=args.project_name,
            goal=args.goal,
            context=args.context,
            directions=json.loads(args.directions_json),
        )
        print(json.dumps({"path": str(repo_root / ".smallest-human-action" / "directions.json"), "directions": len(state["directions"])}, ensure_ascii=False))
        return 0

    if args.command == "show":
        item = append_history(repo_root, direction_id=args.direction_id, event="shown", action=args.action)
        print(json.dumps(item, ensure_ascii=False))
        return 0

    event_name = "skipped" if args.command == "skip" else args.command
    item = mark_latest_event(repo_root, event=event_name, result=args.result)
    print(json.dumps(item, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
