import json
import tempfile
import unittest
from pathlib import Path

from directions_state import (
    append_history,
    create_initial_state,
    load_state,
    mark_latest_event,
    migrate_legacy_state,
    validate_state,
)


class DirectionsStateTest(unittest.TestCase):
    def test_create_initial_state_writes_repo_local_directions_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            state = create_initial_state(
                repo,
                project_name="Test Project",
                goal="Help the user choose directions and take one small action.",
                context=["The user is low energy."],
                directions=[
                    {
                        "title": "Choose the first audience",
                        "whyItMatters": "The product depends on a specific first user.",
                        "userOnlyReason": "Only the user can decide who they want to serve.",
                        "energy": "medium",
                        "clarity": "fuzzy",
                        "resistance": "medium",
                        "actionSeeds": ["Write three possible audiences without choosing."],
                    }
                ],
            )

            path = repo / ".smallest-human-action" / "directions.json"
            self.assertTrue(path.exists())
            self.assertEqual(state["project"]["name"], "Test Project")
            self.assertEqual(state["directions"][0]["status"], "open")
            self.assertEqual(load_state(repo)["directions"][0]["title"], "Choose the first audience")
            self.assertEqual(load_state(repo)["directions"][0]["actionSeeds"], ["Write three possible audiences without choosing."])
            self.assertEqual(load_state(repo)["directions"][0]["actions"], [])

    def test_validate_requires_user_only_reason(self):
        state = {
            "version": 1,
            "project": {"name": "P", "goal": "G", "context": [], "agentBoundary": "Boundary"},
            "directions": [
                {
                    "id": "direction_1",
                    "title": "Choose",
                    "whyItMatters": "It matters.",
                    "status": "open",
                    "energy": "low",
                    "clarity": "clear",
                    "resistance": "low",
                    "actionSeeds": ["Write one word."],
                    "actions": [],
                    "notes": [],
                    "createdAt": "2026-05-23T00:00:00.000Z",
                    "updatedAt": "2026-05-23T00:00:00.000Z",
                    "lastTouchedAt": None,
                }
            ],
            "history": [],
        }

        errors = validate_state(state)

        self.assertIn("directions[0].userOnlyReason is required", errors)

    def test_append_history_records_shown_event(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            create_initial_state(
                repo,
                project_name="Test Project",
                goal="Goal",
                context=[],
                directions=[
                    {
                        "title": "Name the moment",
                        "whyItMatters": "The product needs a crisp moment.",
                        "userOnlyReason": "Only the user knows the lived moment.",
                        "energy": "low",
                        "clarity": "clear",
                        "resistance": "low",
                        "actionSeeds": ["Write one rough sentence."],
                    }
                ],
            )

            event = append_history(repo, direction_id="direction_1", event="shown", action="Write one rough sentence.")
            state = json.loads((repo / ".smallest-human-action" / "directions.json").read_text())

            self.assertEqual(event["event"], "shown")
            self.assertEqual(state["history"][0]["directionId"], "direction_1")
            self.assertEqual(state["history"][0]["actionId"], "action_1")
            self.assertEqual(state["directions"][0]["actions"][0]["text"], "Write one rough sentence.")
            self.assertEqual(state["directions"][0]["actions"][0]["status"], "shown")

    def test_mark_latest_event_done_updates_direction_touch_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            create_initial_state(
                repo,
                project_name="Test Project",
                goal="Goal",
                context=[],
                directions=[
                    {
                        "title": "Name the moment",
                        "whyItMatters": "The product needs a crisp moment.",
                        "userOnlyReason": "Only the user knows the lived moment.",
                        "energy": "low",
                        "clarity": "clear",
                        "resistance": "low",
                        "actionSeeds": ["Write one rough sentence."],
                    }
                ],
            )
            append_history(repo, direction_id="direction_1", event="shown", action="Write one rough sentence.")

            mark_latest_event(repo, event="done", result="User wrote the sentence.")
            state = load_state(repo)

            self.assertEqual(state["history"][-1]["event"], "done")
            self.assertEqual(state["history"][-1]["result"], "User wrote the sentence.")
            self.assertEqual(state["history"][-1]["actionId"], "action_1")
            self.assertEqual(state["directions"][0]["actions"][0]["status"], "done")
            self.assertEqual(state["directions"][0]["actions"][0]["result"], "User wrote the sentence.")
            self.assertIsNotNone(state["directions"][0]["lastTouchedAt"])

    def test_too_hard_updates_latest_action_under_direction(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            create_initial_state(
                repo,
                project_name="Test Project",
                goal="Goal",
                context=[],
                directions=[
                    {
                        "title": "Shape the demo story",
                        "whyItMatters": "The product needs a concrete story.",
                        "userOnlyReason": "Only the user can choose the story they believe.",
                        "energy": "medium",
                        "clarity": "fuzzy",
                        "resistance": "medium",
                    }
                ],
            )
            append_history(repo, direction_id="direction_1", event="shown", action="Write the first sentence.")

            mark_latest_event(repo, event="too_hard", result="Still too vague.")
            state = load_state(repo)

            self.assertEqual(state["directions"][0]["actions"][0]["status"], "too_hard")
            self.assertEqual(state["directions"][0]["actions"][0]["result"], "Still too vague.")

    def test_in_progress_updates_latest_action_under_direction(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            create_initial_state(
                repo,
                project_name="Test Project",
                goal="Goal",
                context=[],
                directions=[
                    {
                        "title": "Shape the demo story",
                        "whyItMatters": "The product needs a concrete story.",
                        "userOnlyReason": "Only the user can choose the story they believe.",
                        "energy": "medium",
                        "clarity": "fuzzy",
                        "resistance": "medium",
                    }
                ],
            )
            append_history(repo, direction_id="direction_1", event="shown", action="Write the first sentence.")

            mark_latest_event(repo, event="in_progress", result="User wants the agent to help in this session.")
            state = load_state(repo)

            self.assertEqual(state["history"][-1]["event"], "in_progress")
            self.assertEqual(state["directions"][0]["actions"][0]["status"], "in_progress")
            self.assertEqual(state["directions"][0]["actions"][0]["result"], "User wants the agent to help in this session.")

    def test_migrate_legacy_moves_to_directions(self):
        legacy_state = {
            "version": 1,
            "project": {"name": "Old Project", "goal": "Old goal", "context": ["Old context"], "agentBoundary": "Old boundary"},
            "moves": [
                {
                    "id": "move_1",
                    "title": "Shape the demo story",
                    "whyItMatters": "It helps people understand the product.",
                    "userOnlyReason": "Only the user can decide the story they believe.",
                    "status": "open",
                    "energy": "medium",
                    "clarity": "fuzzy",
                    "resistance": "medium",
                    "smallestAction": "Write the first sentence.",
                    "notes": [],
                    "createdAt": "2026-05-23T00:00:00.000Z",
                    "updatedAt": "2026-05-23T00:00:00.000Z",
                    "lastTouchedAt": None,
                }
            ],
            "history": [
                {
                    "id": "hist_1",
                    "moveId": "move_1",
                    "event": "shown",
                    "action": "Write the first sentence.",
                    "result": None,
                    "createdAt": "2026-05-23T00:00:00.000Z",
                }
                ,
                {
                    "id": "hist_2",
                    "moveId": "move_1",
                    "event": "done",
                    "action": "Write the first sentence.",
                    "result": "User wrote it.",
                    "createdAt": "2026-05-23T00:01:00.000Z",
                }
            ],
        }

        state = migrate_legacy_state(legacy_state)

        self.assertEqual(state["directions"][0]["id"], "move_1")
        self.assertEqual(state["directions"][0]["actionSeeds"], ["Write the first sentence."])
        self.assertEqual(state["directions"][0]["actions"][0]["text"], "Write the first sentence.")
        self.assertEqual(state["directions"][0]["actions"][0]["status"], "done")
        self.assertEqual(state["directions"][0]["actions"][0]["result"], "User wrote it.")
        self.assertEqual(state["history"][0]["directionId"], "move_1")
        self.assertEqual(state["history"][0]["actionId"], "action_1")
        self.assertEqual(state["history"][1]["actionId"], "action_1")
        self.assertNotIn("moveId", state["history"][0])


if __name__ == "__main__":
    unittest.main()
