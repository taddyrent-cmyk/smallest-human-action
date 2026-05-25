import tempfile
import unittest
from pathlib import Path

from directions_state import append_history, create_initial_state, load_state, mark_latest_event
from visualize_directions import render_state


class VisualizeDirectionsTest(unittest.TestCase):
    def test_render_state_shows_directions_actions_and_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            create_initial_state(
                repo,
                project_name="Demo Project",
                goal="Make the project less stuck.",
                context=[],
                directions=[
                    {
                        "title": "Shape the demo story",
                        "whyItMatters": "People need to understand the project.",
                        "userOnlyReason": "Only the user can choose the story they believe.",
                        "energy": "medium",
                        "clarity": "fuzzy",
                        "resistance": "medium",
                    }
                ],
            )
            append_history(repo, "direction_1", "shown", "Write the first demo sentence.")
            mark_latest_event(repo, "in_progress", "User wants help in this session.")

            output = render_state(load_state(repo))

            self.assertIn("# Smallest Human Action Map", output)
            self.assertIn("Project: Demo Project", output)
            self.assertIn("### [open] Shape the demo story", output)
            self.assertIn("| in_progress | Write the first demo sentence. | User wants help in this session.", output)
            self.assertIn("## Recent Timeline", output)


if __name__ == "__main__":
    unittest.main()
