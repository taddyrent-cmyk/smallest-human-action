#!/usr/bin/env python3
import sys
from pathlib import Path

from directions_state import load_state


def one_line(value):
    if value is None:
        return ""
    return " ".join(str(value).split())


def render_state(state):
    project = state.get("project", {})
    directions = state.get("directions", [])
    history = state.get("history", [])

    lines = [
        "# Smallest Human Action Map",
        "",
        f"Project: {one_line(project.get('name', 'Project'))}",
        f"Goal: {one_line(project.get('goal', ''))}",
        "",
        "## Summary",
        "",
    ]

    direction_counts = count_by_status(directions)
    actions = [action for direction in directions for action in direction.get("actions", [])]
    action_counts = count_by_status(actions)

    lines.extend(
        [
            f"- Directions: {len(directions)} total, {format_counts(direction_counts)}",
            f"- Actions: {len(actions)} total, {format_counts(action_counts)}",
            "",
            "## Directions",
            "",
        ]
    )

    if not directions:
        lines.append("No directions captured yet.")
    for direction in directions:
        lines.extend(render_direction(direction))

    if history:
        lines.extend(["", "## Recent Timeline", ""])
        for item in history[-8:]:
            action_ref = f", action {item.get('actionId')}" if item.get("actionId") else ""
            result = f" - {one_line(item.get('result'))}" if item.get("result") else ""
            lines.append(
                f"- {item.get('createdAt')}: {item.get('event')} on {item.get('directionId')}{action_ref}{result}"
            )

    return "\n".join(lines).rstrip() + "\n"


def count_by_status(items):
    counts = {}
    for item in items:
        status = item.get("status", "unknown")
        counts[status] = counts.get(status, 0) + 1
    return counts


def format_counts(counts):
    if not counts:
        return "none"
    return ", ".join(f"{status} {count}" for status, count in sorted(counts.items()))


def render_direction(direction):
    lines = [
        f"### [{direction.get('status')}] {one_line(direction.get('title'))}",
        "",
        f"- Why: {one_line(direction.get('whyItMatters'))}",
        f"- User-owned because: {one_line(direction.get('userOnlyReason'))}",
        f"- State: energy {direction.get('energy')}, clarity {direction.get('clarity')}, resistance {direction.get('resistance')}",
    ]

    notes = direction.get("notes", [])
    if notes:
        lines.append(f"- Notes: {one_line(notes[-1])}")

    lines.extend(["", "| Action Status | Action | Result | Updated |", "| --- | --- | --- | --- |"])
    actions = direction.get("actions", [])
    if actions:
        for action in actions:
            lines.append(
                "| "
                + " | ".join(
                    [
                        one_line(action.get("status")),
                        one_line(action.get("text")),
                        one_line(action.get("result")),
                        one_line(action.get("updatedAt")),
                    ]
                )
                + " |"
            )
    else:
        lines.append("| none | No actions shown yet |  |  |")

    lines.append("")
    return lines


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    state = load_state(repo_root)
    print(render_state(state), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
