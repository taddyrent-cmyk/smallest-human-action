import json
from datetime import datetime, timezone
from pathlib import Path


STATE_DIR = ".smallest-human-action"
STATE_FILE = "directions.json"
LEGACY_STATE_DIR = ".one-human-move"
LEGACY_STATE_FILE = "moves.json"

DIRECTION_STATUSES = {"open", "in_progress", "resolved", "parked"}
ENERGY_LEVELS = {"low", "medium", "high"}
CLARITY_LEVELS = {"clear", "fuzzy", "blocked"}
HISTORY_EVENTS = {"shown", "in_progress", "done", "too_hard", "skipped", "not_now", "note"}
ACTION_STATUSES = {"shown", "in_progress", "done", "too_hard", "skipped", "not_now"}


def state_path(repo_root):
    return Path(repo_root) / STATE_DIR / STATE_FILE


def legacy_state_path(repo_root):
    return Path(repo_root) / LEGACY_STATE_DIR / LEGACY_STATE_FILE


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def create_initial_state(repo_root, project_name, goal, context, directions):
    timestamp = now_iso()
    normalized_directions = []

    for index, direction in enumerate(directions, start=1):
        normalized_directions.append(normalize_direction(direction, index, timestamp))

    state = {
        "version": 1,
        "project": {
            "name": project_name,
            "goal": goal,
            "context": context,
            "agentBoundary": "The agent does tasks. The human chooses directions and takes actions.",
        },
        "directions": normalized_directions,
        "history": [],
    }

    errors = validate_state(state)
    if errors:
        raise ValueError("; ".join(errors))

    save_state(repo_root, state)
    return state


def normalize_direction(direction, index, timestamp):
    return {
        "id": direction.get("id") or f"direction_{index}",
        "title": direction["title"],
        "whyItMatters": direction["whyItMatters"],
        "userOnlyReason": direction["userOnlyReason"],
        "status": direction.get("status", "open"),
        "energy": direction.get("energy", "medium"),
        "clarity": direction.get("clarity", "fuzzy"),
        "resistance": direction.get("resistance", "medium"),
        "actionSeeds": direction.get("actionSeeds") or ([direction["smallestAction"]] if direction.get("smallestAction") else []),
        "actions": direction.get("actions", []),
        "notes": direction.get("notes", []),
        "createdAt": direction.get("createdAt", timestamp),
        "updatedAt": direction.get("updatedAt", timestamp),
        "lastTouchedAt": direction.get("lastTouchedAt"),
    }


def load_state(repo_root):
    path = state_path(repo_root)
    if path.exists():
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    legacy_path = legacy_state_path(repo_root)
    if legacy_path.exists():
        with legacy_path.open("r", encoding="utf-8") as file:
            legacy_state = json.load(file)
        state = migrate_legacy_state(legacy_state)
        save_state(repo_root, state)
        return state

    raise FileNotFoundError(path)


def migrate_legacy_state(legacy_state):
    timestamp = now_iso()
    directions = [
        normalize_direction(move, index, timestamp)
        for index, move in enumerate(legacy_state.get("moves", []), start=1)
    ]
    history = []
    for item in legacy_state.get("history", []):
        migrated = migrate_legacy_history_item(item, directions)
        history.append(migrated)

    project = legacy_state.get("project", {})
    return {
        "version": 1,
        "project": {
            "name": project.get("name", "Project"),
            "goal": project.get("goal", ""),
            "context": project.get("context", []),
            "agentBoundary": "The agent does tasks. The human chooses directions and takes actions.",
        },
        "directions": directions,
        "history": history,
    }


def migrate_legacy_history_item(item, directions):
    migrated = dict(item)
    if "moveId" in migrated and "directionId" not in migrated:
        migrated["directionId"] = migrated.pop("moveId")

    direction = find_direction({"directions": directions}, migrated.get("directionId"))
    if direction and migrated.get("event") == "shown":
        action = create_action(direction, migrated.get("action", ""), migrated.get("createdAt") or now_iso())
        migrated["actionId"] = action["id"]
    elif direction and migrated.get("event") in ACTION_STATUSES:
        action = latest_action(direction)
        if action:
            action["status"] = migrated["event"]
            action["result"] = migrated.get("result")
            action["updatedAt"] = migrated.get("createdAt") or now_iso()
            migrated["actionId"] = action["id"]

    return migrated


def save_state(repo_root, state):
    path = state_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_state(state):
    errors = []

    if state.get("version") != 1:
        errors.append("version must be 1")

    project = state.get("project")
    if not isinstance(project, dict):
        errors.append("project is required")
    else:
        for field in ("name", "goal", "context", "agentBoundary"):
            if field not in project:
                errors.append(f"project.{field} is required")

    directions = state.get("directions")
    if not isinstance(directions, list):
        errors.append("directions must be an array")
        directions = []

    for index, direction in enumerate(directions):
        for field in ("id", "title", "whyItMatters", "userOnlyReason", "status", "energy", "clarity", "resistance", "actions", "notes", "createdAt", "updatedAt"):
            if field not in direction:
                errors.append(f"directions[{index}].{field} is required")

        if direction.get("status") not in DIRECTION_STATUSES:
            errors.append(f"directions[{index}].status is invalid")
        if direction.get("energy") not in ENERGY_LEVELS:
            errors.append(f"directions[{index}].energy is invalid")
        if direction.get("clarity") not in CLARITY_LEVELS:
            errors.append(f"directions[{index}].clarity is invalid")
        if direction.get("resistance") not in ENERGY_LEVELS:
            errors.append(f"directions[{index}].resistance is invalid")
        if "actionSeeds" in direction and not isinstance(direction["actionSeeds"], list):
            errors.append(f"directions[{index}].actionSeeds must be an array")
        if "actions" in direction and not isinstance(direction["actions"], list):
            errors.append(f"directions[{index}].actions must be an array")
        for action_index, action in enumerate(direction.get("actions", [])):
            for field in ("id", "text", "status", "result", "createdAt", "updatedAt"):
                if field not in action:
                    errors.append(f"directions[{index}].actions[{action_index}].{field} is required")
            if action.get("status") not in ACTION_STATUSES:
                errors.append(f"directions[{index}].actions[{action_index}].status is invalid")
        if "notes" in direction and not isinstance(direction["notes"], list):
            errors.append(f"directions[{index}].notes must be an array")

    history = state.get("history")
    if not isinstance(history, list):
        errors.append("history must be an array")
        history = []

    for index, item in enumerate(history):
        for field in ("id", "directionId", "event", "result", "createdAt"):
            if field not in item:
                errors.append(f"history[{index}].{field} is required")
        if item.get("event") not in HISTORY_EVENTS:
            errors.append(f"history[{index}].event is invalid")

    return errors


def append_history(repo_root, direction_id, event, action, result=None):
    if event not in HISTORY_EVENTS:
        raise ValueError(f"Unsupported event: {event}")

    state = load_state(repo_root)
    timestamp = now_iso()
    history_id = f"hist_{len(state.get('history', [])) + 1}"
    history_item = {
        "id": history_id,
        "directionId": direction_id,
        "event": event,
        "result": result,
        "createdAt": timestamp,
    }

    direction = find_direction(state, direction_id)
    if direction:
        if event == "shown":
            action_item = create_action(direction, action, timestamp)
            history_item["actionId"] = action_item["id"]
        elif event in ACTION_STATUSES:
            action_item = latest_action(direction)
            if action_item:
                action_item["status"] = event
                action_item["result"] = result
                action_item["updatedAt"] = timestamp
                history_item["actionId"] = action_item["id"]
        direction["updatedAt"] = timestamp
        if event in {"shown", "in_progress", "done", "too_hard", "skipped", "not_now"}:
            direction["lastTouchedAt"] = timestamp

    state.setdefault("history", []).append(history_item)
    save_state(repo_root, state)
    return history_item


def mark_latest_event(repo_root, event, result=None):
    if event not in HISTORY_EVENTS:
        raise ValueError(f"Unsupported event: {event}")

    state = load_state(repo_root)
    shown_events = [item for item in state.get("history", []) if item.get("event") == "shown"]
    if not shown_events:
        raise ValueError("No shown event to update")

    latest = shown_events[-1]
    direction_id = latest.get("directionId") or latest.get("moveId")
    timestamp = now_iso()
    item = {
        "id": f"hist_{len(state.get('history', [])) + 1}",
        "directionId": direction_id,
        "event": event,
        "result": result,
        "createdAt": timestamp,
    }

    direction = find_direction(state, direction_id)
    if direction:
        action = find_action(direction, latest.get("actionId")) or latest_action(direction)
        if action:
            action["status"] = event
            action["result"] = result
            action["updatedAt"] = timestamp
            item["actionId"] = action["id"]
        direction["updatedAt"] = timestamp
        direction["lastTouchedAt"] = timestamp

    state["history"].append(item)
    save_state(repo_root, state)
    return item


def find_direction(state, direction_id):
    for direction in state.get("directions", []):
        if direction.get("id") == direction_id:
            return direction
    return None


def create_action(direction, text, timestamp):
    action = {
        "id": f"action_{len(direction.get('actions', [])) + 1}",
        "text": text,
        "status": "shown",
        "result": None,
        "createdAt": timestamp,
        "updatedAt": timestamp,
    }
    direction.setdefault("actions", []).append(action)
    return action


def latest_action(direction):
    actions = direction.get("actions", [])
    return actions[-1] if actions else None


def find_action(direction, action_id):
    if not action_id:
        return None
    for action in direction.get("actions", []):
        if action.get("id") == action_id:
            return action
    return None
