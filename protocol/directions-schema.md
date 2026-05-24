# Smallest Human Action State Schema

State lives in the current repo at:

```text
.smallest-human-action/directions.json
```

Treat `.smallest-human-action/` as private local state by default. Add it to `.gitignore` unless the user explicitly wants to share the directions file.

Older `.one-human-move/moves.json` files may be migrated into this shape.

## Shape

```json
{
  "version": 1,
  "project": {
    "name": "Project name",
    "goal": "Short project goal",
    "context": ["Durable project context"],
    "agentBoundary": "The agent does tasks. The human chooses directions and takes actions."
  },
  "directions": [
    {
      "id": "direction_1",
      "title": "Shape the demo story",
      "whyItMatters": "The demo affects whether real people understand why the project matters.",
      "userOnlyReason": "Only the user can decide the story they believe and want to tell.",
      "status": "open",
      "energy": "medium",
      "clarity": "fuzzy",
      "resistance": "medium",
      "actionSeeds": [
        "Possible future action: write the first sentence of the voiceover."
      ],
      "actions": [
        {
          "id": "action_1",
          "text": "Write the first sentence of the voiceover. Stop there.",
          "status": "done",
          "result": "User wrote a rough first sentence.",
          "createdAt": "2026-05-23T00:00:00.000Z",
          "updatedAt": "2026-05-23T00:01:00.000Z"
        }
      ],
      "notes": [],
      "createdAt": "2026-05-23T00:00:00.000Z",
      "updatedAt": "2026-05-23T00:00:00.000Z",
      "lastTouchedAt": null
    }
  ],
  "history": [
    {
      "id": "hist_1",
      "directionId": "direction_1",
      "actionId": "action_1",
      "event": "shown",
      "result": null,
      "createdAt": "2026-05-23T00:00:00.000Z"
    }
  ]
}
```

## Required Direction Fields

- `id`
- `title`
- `whyItMatters`
- `userOnlyReason`
- `status`
- `energy`
- `clarity`
- `resistance`
- `actions`
- `notes`
- `createdAt`
- `updatedAt`
- `lastTouchedAt`

`userOnlyReason` is mandatory. If the agent cannot explain why the user must own the direction, it is probably an agent task, not a Direction.

`actionSeeds` is optional. When present, it is an array of future action material. It is not the action to show automatically during capture. When the user asks for an action, generate the actual Smallest Human Action from repo context, current thread context, the selected Direction, and the user's present state.

`actions` is the canonical record of suggested actions under a Direction. Store every shown action here with its own status and result. This lets the agent see how this Direction has progressed and avoid repeating stale suggestions.

## Allowed Values

`status`:

```text
open
in_progress
resolved
parked
```

`energy` and `resistance`:

```text
low
medium
high
```

`clarity`:

```text
clear
fuzzy
blocked
```

`history[].event`:

```text
shown
done
too_hard
skipped
not_now
note
```

`history` is a cross-Direction event timeline. It should reference `directionId` and, when applicable, `actionId`. It is not the canonical place to store action text or action status.

Both `directions[].actions[]` and `history[]` are inputs to future action generation. The agent should use recent `shown`, `done`, `too_hard`, `skipped`, `not_now`, and `note` events to avoid repetition, shrink actions that were too hard, deprioritize skipped Directions, and incorporate user realizations.
