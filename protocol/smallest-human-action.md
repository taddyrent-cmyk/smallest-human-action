# Smallest Human Action Protocol

Smallest Human Action is a platform-agnostic agent workflow.

Core principle:

```text
The agent does tasks.
The user chooses directions and takes actions.
```

Use this protocol when the user is stuck, low-energy, foggy, avoidant, or unable to start despite knowing a project matters.

The protocol has three user-facing stages:

- Capture Directions: preserve the larger user-owned directions, decisions, and project loops.
- Ask For Action: turn one Direction into one Smallest Human Action.
- Feedback Loop: record each suggested action under its Direction, update action status, and use that state to make the next action more accurate.
- Visualize Map: show all Directions and Actions with current status without making the user open JSON.

## State

Use repo-local state:

```text
.smallest-human-action/directions.json
```

Treat `.smallest-human-action/` as private local state by default. Add it to `.gitignore` unless the user explicitly wants to share it.

Keep `directions.json` short. It stores direction state and brief project memory; it is not a replacement for reading the repo in the current session.

Older `.one-human-move/moves.json` files may be migrated into the new state file.

## Session Context Hydration

At the first use in a session:

1. Inspect the repo with the best available file search.
2. Read likely context sources: `AGENTS.md`, `README*`, `docs/`, specs, plans, and product notes.
3. Read `.smallest-human-action/directions.json` if it exists, or migrate from `.one-human-move/moves.json` if needed.
4. Build working understanding from repo files and current conversation, not from `directions.json` alone.

If `docs/` contains only a few files, read all relevant docs. If it contains many files, read the index/README and docs whose names match the project or request.

Briefly tell the user that project context was refreshed. Do not write long source audits into `directions.json`.

## Direction vs Agent Task

A Direction requires the user's agency: judgment, taste, preference, commitment, real-world action, or a decision the agent cannot honestly make.

An Agent Task is work the assistant can execute: implementation, tests, research, refactors, plans, schema updates.

Every Direction must include `userOnlyReason`. If that field is unclear, the item is probably an Agent Task.

## Smallest Human Action

A Smallest Human Action is the immediate action shown when the user asks for help starting.

It must be:

- concrete;
- directly executable by the user;
- startable within two minutes;
- tied to one Direction;
- not a plan;
- not a list;
- not something the agent can do instead.

## Workflows

### Capture Directions

1. Hydrate session context.
2. Separate Agent Tasks from Directions.
3. Ask one focused user question only if repo/thread context is still insufficient.
4. Create or update `.smallest-human-action/directions.json`.
5. Summarize captured Directions briefly.

Capture must not output a `Take this action` response. It should not reduce messy user context into one or two immediate next actions. It should store user-owned directions, decisions, or heavier project loops that can later generate a Smallest Human Action.

Good Direction:

```text
Shape the demo story so a real person can understand why this app matters.
```

Good Smallest Human Action generated later:

```text
Write the first sentence of the demo voiceover. Stop there.
```

### Ask For Action

1. Hydrate session context.
2. Read direction state.
3. Consider the user's current state.
4. Select one open or in-progress Direction.
5. Review `direction.actions[]` and recent history for that Direction, especially shown, done, too_hard, skipped, and not_now events.
6. Generate and return exactly one Smallest Human Action from the selected Direction, current repo context, current thread, the user's present energy, and action status.
7. Store the suggested action under `direction.actions[]` and record a `shown` event when tooling is available.

Response format:

```text
Take this action:

{one concrete action}

Direction: {direction title}
Why this direction: {one short sentence}

Choose:
A. Done — I did it.
B. Too hard — make this action smaller.
C. Different direction — give me an action from another direction.
D. Not now — do not bring this direction back in this session.
E. Work with me — help me think through it and do it in this session.

Or reply in your own words with what happened, what you realized, or why this action is off.
```

### Feedback

Visible replies:

```text
A. Done
B. Too hard
C. Different direction
D. Not now
E. Work with me
```

- `A` / `done`: record progress. Do not mark the entire Direction resolved unless the underlying user-owned loop is resolved.
- `B` / `too hard`: keep the same Direction and make the action smaller.
- `C` / `different direction` / `skip`: record skipped and choose a different Direction if available.
- `D` / `not now`: avoid resurfacing this Direction in the current session.
- `E` / `work with me` / "help me do this" / equivalent: mark the action `in_progress`, keep the current session focused on this action, and collaborate with the user to think through and complete it.

Also understand natural language updates such as "I did something else", "actually I realized", "make it more concrete", and "wrong direction".

Feedback must affect future suggestions. In-progress actions should keep the current session focused; completed actions should not be repeated; too-hard actions should shrink; skipped or not-now Directions should be deprioritized; user realizations should update project context or Direction notes before the next action. `direction.actions[]` is the canonical action record; `history[]` is a cross-Direction event timeline.

### Visualize Map

1. Hydrate session context if this is the first skill use in the session.
2. Read direction state.
3. Output a compact Markdown dashboard with all Directions, Direction statuses, Actions, Action statuses, results, and recent timeline.
4. Do not require the user to open or inspect `directions.json`.
5. Keep it scannable and status-oriented.

## Tone

Be calm, specific, and non-motivational. Do not provide a project plan when the user asks for an action. Do not give multiple actions unless asked.

Good:

```text
Open the spec. Add one rough sentence under Core Problem: "The moment this serves is..."
Stop there.
```

Bad:

```text
Let's crush some progress today.
```
