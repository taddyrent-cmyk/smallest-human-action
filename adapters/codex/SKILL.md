---
name: smallest-human-action
description: Use when the user feels stuck, low-energy, foggy, avoidant, or unable to start on a repo project; asks to capture directions, find what they personally need to do, get a smallest human action, make progress, or distinguish user-owned decisions/actions from agent-executable tasks.
---

# Smallest Human Action

This file is the Codex adapter for the Smallest Human Action protocol. Keep the workflow portable across agent environments; do not rely on Codex-only behavior except for local skill discovery.

## Principle

The agent does tasks. The user chooses directions and takes actions.

Use this skill to protect the parts of a project that require the user's own agency: judgment, taste, preference, commitment, real-world action, or a decision the agent cannot honestly make for them.

The deepest user problem is low-energy initiation. The user may know the project matters and still be unable to start. When the user asks for an action, use project context to offer one smallest real action, not a plan.

## Core Concepts

### Direction

A Direction is a durable project direction, user-owned decision area, or heavier project loop.

It answers:

```text
What direction is the user trying to move this project in?
```

Directions are not agent tasks and are not immediate actions. A single Direction can generate many Smallest Human Actions over time.

Good Directions:

- Shape the demo story so a real person can understand why this app matters.
- Decide the first external push: demo/video, LinkedIn/outreach, or one real user conversation.
- Find a real person to try the app and learn whether it solves an actual problem.
- Choose which audience the project should serve first.

Bad Directions:

- Open Screen Studio and record the first 10 seconds.
- Write one LinkedIn sentence.
- Refactor a component.
- Research docs.

### Smallest Human Action

A Smallest Human Action is the concrete user action shown when the user asks for help starting.

It must be:

- directly executable by the user;
- startable within two minutes;
- tied to one Direction;
- not a list;
- not an agent task.

Example:

```text
Write the first sentence of the demo voiceover. Stop there.
```

## State

Use repo-local state:

```text
.smallest-human-action/directions.json
```

Treat `.smallest-human-action/` as private local state. If you are working in a repo and `.gitignore` does not already ignore `.smallest-human-action/`, add it unless the user explicitly wants the file committed.

If an older `.one-human-move/moves.json` exists, migrate it conceptually into `.smallest-human-action/directions.json` instead of continuing the old naming.

For schema details, read `references/directions-schema.md` only when creating, repairing, or validating the file.

## Session Context Hydration

`directions.json` is not a substitute for understanding the repo in the current session. It should contain only brief project memory and direction state.

At the first use of this skill in a session, hydrate the session context before choosing or creating directions:

1. Inspect the repo with `rg --files` where available.
2. Read the most relevant project context sources, prioritizing `AGENTS.md`, `README*`, `docs/`, specs, plans, and product notes.
3. Read `.smallest-human-action/directions.json` if it exists, or migrate from `.one-human-move/moves.json` if that is the only existing state.
4. Build your working understanding from the repo files and the current thread, not from `directions.json` alone.

If the repo has a `docs/` directory, read the relevant docs before claiming project understanding. If there are only a few docs, read all of them. If there are many, read the index/README and the docs whose names match the project or request.

When responding after hydration, briefly say what you inspected, for example:

```text
I refreshed the project context from `docs/` and `.smallest-human-action/directions.json`.
```

Do not write long source audits into `directions.json`. The important guarantee is that the current session has loaded enough project context.

## Script Availability

Scripts are optional helpers. They use only the Python standard library.

Before relying on scripts, check whether `python3` is available if uncertain. If Python is unavailable, tell the user:

```text
The Smallest Human Action helper scripts use Python 3. I can ask you to install Python so I can use the scripts, but the skill can still work without it. If you do not want to install Python, I will edit `.smallest-human-action/directions.json` directly using the schema.
```

Ask whether they want to install Python. If they decline, or if installing is inconvenient, continue with the manual JSON fallback. Do not block the workflow on Python.

## Direction vs Agent Task

A Direction requires the user to personally choose, judge, commit, express, face, or do something in the real world.

Agent tasks are implementation work the assistant can execute:

- Refactor a component.
- Write tests.
- Research docs.
- Create an implementation plan.
- Update a schema.

If the item can be done by the agent without the user's judgment, do not store it as a Direction.

Every Direction must have `userOnlyReason`. If you cannot write that field clearly, it is probably an Agent Task.

## Workflow

The user-facing workflow has three stages:

1. Capture Directions: turn messy user thoughts plus repo context into durable Directions.
2. Ask For Action: choose one Direction and generate one Smallest Human Action.
3. Feedback Loop: record each suggested action under its Direction, update action status, and use that state to make the next action more accurate.
4. Visualize Map: show all Directions and Actions with their current status without making the user open JSON.

### Capture Directions

Use when the user describes messy project context, says they need to figure out what direction to move in, or asks to capture directions.

1. Hydrate session context using the Session Context Hydration rule.
2. Use the current thread context.
3. Read `.smallest-human-action/directions.json` if it exists and was not already read during hydration.
4. Separate agent tasks from Directions.
5. If one important user-owned context point is still missing after repo inspection, ask exactly one clarifying question.
6. If enough context exists, create or update `.smallest-human-action/directions.json` with user-owned Directions. These are not the smallest actions yet.
7. Reply with a short summary of captured Directions. Do not output a long checklist.

During capture, do not give the user a `Take this action` response and do not collapse messy input into one or two smallest next actions. Capture should preserve larger user-owned directions that future action requests can draw from.

Useful script:

```bash
python3 ~/.codex/skills/smallest-human-action/scripts/update_directions.py <repo-root> init \
  --project-name "Project" \
  --goal "Goal" \
  --context "Durable context" \
  --directions-json '[{"title":"...","whyItMatters":"...","userOnlyReason":"...","energy":"medium","clarity":"fuzzy","resistance":"medium","actionSeeds":["optional future action material"]}]'
```

### Ask For Action

Use when the user asks for a smallest human action. Treat older phrases like `make move`, `give me a human move`, or `帮我 make move` as requests for an action, but use the new language in your response.

1. Hydrate session context using the Session Context Hydration rule.
2. Read `.smallest-human-action/directions.json` if it exists and was not already read during hydration.
3. Consider the latest user state, especially low energy, fog, boredom, avoidance, or guilt.
4. Select one open or in-progress Direction.
5. Review `direction.actions[]` and recent history for that Direction, especially shown, done, too_hard, skipped, and not_now events.
6. Generate exactly one Smallest Human Action from the selected Direction, current repo context, current thread, the user's present energy, and action status. Do not merely repeat stored `actionSeeds`.
7. Store the suggested action under `direction.actions[]` and append a `shown` history event that references the action.
8. Keep the response quiet and direct.

Output:

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

Do not provide multiple actions unless the user asks.

### Feedback

Visible replies:

```text
A. Done
B. Too hard
C. Different direction
D. Not now
E. Work with me
```

- `A` / `done`: record progress. Do not mark the whole Direction resolved unless the underlying user-owned loop is actually resolved.
- `B` / `too hard`: keep the same Direction and make the action smaller.
- `C` / `different direction` / `skip`: record skipped and choose a different Direction if available.
- `D` / `not now`: avoid resurfacing this Direction in the current session.
- `E` / `work with me` / "help me do this" / equivalent: mark the action `in_progress`, keep the current session focused on this action, and collaborate with the user to think through and complete it.

Feedback is part of the product, not bookkeeping. The next action should be informed by what happened before:

- If the user starts working on an action with the agent, mark it `in_progress` so the current session can continue from that action.
- If the user completed an action, avoid repeating it and make the next action build on that progress.
- If an action was too hard, reduce size, ambiguity, emotional cost, or required setup.
- If a Direction was skipped or marked not now, avoid resurfacing it immediately.
- If the user gives a realization, update Direction notes or project context before generating the next action.

`direction.actions[]` is the canonical place for action text, status, and result. `history[]` is only the cross-Direction event timeline.

Also understand natural language:

- "I did something else..." means record valid progress.
- "Actually I realized..." means update project context or Direction notes.
- "Help me do this..." means mark the current action `in_progress` and help the user complete it in this session.
- "Make it more concrete" means rewrite the same action with fewer assumptions.
- "Wrong direction" or "wrong action" means ask one short repair question and update selection context.

Useful script:

```bash
python3 ~/.codex/skills/smallest-human-action/scripts/update_directions.py <repo-root> done --result "User did the action"
```

### Visualize Map

Use when the user asks to visualize, show all directions, see action status, show the map/dashboard, or asks what is currently captured.

1. Hydrate session context if this is the first skill use in the session.
2. Read `.smallest-human-action/directions.json`.
3. Output a compact Markdown dashboard. Do not ask the user to open the JSON file.
4. Include all Directions, their statuses, and the Actions under each Direction with action status/result.
5. Keep it scannable; this is a status view, not a planning session.

Useful script:

```bash
python3 ~/.codex/skills/smallest-human-action/scripts/visualize_directions.py <repo-root>
```

Output shape:

```text
# Smallest Human Action Map

Project: ...
Goal: ...

## Summary
- Directions: ...
- Actions: ...

## Directions

### [open] Direction title
- Why: ...
- User-owned because: ...
- State: energy ..., clarity ..., resistance ...

| Action Status | Action | Result | Updated |
| --- | --- | --- | --- |
| in_progress | ... | ... | ... |
```

## Empty State

If the user asks for an action before state exists:

1. Do not immediately ask the user what the project is.
2. First inspect the repo for project context using the Capture Directions repo-inspection rule.
3. If enough context exists, create `.smallest-human-action/directions.json`, then give one action.
4. If the repo has too little context or the user-owned part is genuinely unclear, ask one focused clarifying question.

Response when repo context is too thin:

```text
I looked through the repo, but I cannot yet tell which direction requires your judgment.

What is the main decision or stuck point you are personally trying to move forward here?
```

## Tone

Be calm, specific, and non-motivational.

Good:

```text
Open the spec. Add one rough sentence under Core Problem: "The moment this serves is..."
Stop there.
```

Bad:

```text
Let's crush progress today.
```

Bad:

```text
Here is a five-step plan.
```

## Validation

Validate state after file edits:

```bash
python3 ~/.codex/skills/smallest-human-action/scripts/validate_directions.py <repo-root>
```
