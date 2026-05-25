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

    lines = [
        "# Direction Map",
        "",
        f"Project: {one_line(project.get('name', 'Project'))}",
    ]
    goal = one_line(project.get("goal", ""))
    if goal:
        lines.append(f"Goal: {goal}")
    lines.append("")

    direction_counts = count_by_status(directions)
    actions = [action for direction in directions for action in direction.get("actions", [])]
    action_counts = count_by_status(actions)
    lines.append(f"Snapshot: {len(directions)} directions ({format_counts(direction_counts)}); {len(actions)} actions ({format_counts(action_counts)})")
    lines.append("")

    if not directions:
        return "\n".join(lines + ["No directions captured yet."]).rstrip() + "\n"

    focus = choose_focus(directions)
    lines.extend(["## Current Focus", ""])
    if focus:
        lines.extend(render_focus(focus))
    else:
        lines.append("No active action yet.")

    lines.extend(["", "## Outline Map", ""])
    for index, direction in enumerate(directions, start=1):
        lines.extend(render_outline_direction(index, direction))

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


def choose_focus(directions):
    priority = {"in_progress": 0, "shown": 1, "too_hard": 2}
    candidates = []
    for direction in directions:
        for action in direction.get("actions", []):
            status = action.get("status")
            if status in priority:
                candidates.append((priority[status], action.get("updatedAt") or "", direction, action))
    if candidates:
        return sorted(candidates, key=lambda item: (item[0], item[1]))[0][2:]

    open_directions = [direction for direction in directions if direction.get("status") in {"open", "in_progress"}]
    if open_directions:
        return (open_directions[0], None)
    return (directions[0], None) if directions else None


def render_focus(focus):
    direction, action = focus
    lines = [
        f"Direction: [{direction.get('status')}] {one_line(direction.get('title'))}",
        f"Why: {one_line(direction.get('whyItMatters'))}",
    ]
    if action:
        lines.append(f"Action: [{action.get('status')}] {one_line(action.get('text'))}")
        if action.get("result"):
            lines.append(f"Last result: {one_line(action.get('result'))}")
    else:
        lines.append("Action: none shown yet")
    return lines


def render_outline_direction(index, direction):
    lines = [f"{index}. [{direction.get('status')}] {one_line(direction.get('title'))}"]
    actions = direction.get("actions", [])
    if not actions:
        lines.append("   - [none] No actions shown yet")
        return lines

    for action in actions[-3:]:
        result = f" - {one_line(action.get('result'))}" if action.get("result") else ""
        lines.append(f"   - [{action.get('status')}] {one_line(action.get('text'))}{result}")
    if len(actions) > 3:
        lines.append(f"   - ... {len(actions) - 3} earlier actions")
    return lines


def main():
    repo_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    state = load_state(repo_root)
    print(render_state(state), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
