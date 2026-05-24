# Smallest Human Action Skill Protocol Spec

## 1. Product Shift

This spec supersedes the original web-first todo MVP and the earlier One Human Move naming.

The product is a repo-local agent skill protocol. It helps the user choose project directions and take one smallest human action when they are stuck, low-energy, foggy, avoidant, or unable to start.

Core principle:

```text
The agent does tasks.
The user chooses directions and takes actions.
```

The old word "move" was too ambiguous: it could mean a large direction, a concrete step, or a tiny action. The protocol now separates those concepts.

## 2. Core Problem

The deepest problem is not that the user lacks things to do. The user often knows the project matters but cannot start.

The user may be:

- low energy;
- foggy;
- bored;
- avoidant;
- tired of deciding;
- surrounded by many possible actions, none of which feel startable.

In that state, a normal todo list creates more friction. It asks the user to read, compare, prioritize, and decide.

The product should solve this moment:

```text
I know this project matters. I cannot make myself start. Give me one smallest human action that moves it forward.
```

The action must come from current project context, not an isolated todo item. It depends on the project goal, recent conversation, unresolved decisions, current blockers, and what the repo already says.

## 3. Core Concepts

### 3.1 Agent Task

An Agent Task is work the assistant can execute:

- implement a feature;
- write tests;
- research docs;
- refactor code;
- create a plan;
- update a schema.

Agent Tasks should not be stored as Directions.

### 3.2 Direction

A Direction is a durable user-owned project direction, decision area, or heavier project loop.

It answers:

```text
What direction is the user trying to move this project in?
```

A Direction may require:

- judgment;
- taste;
- preference;
- commitment;
- real-world action;
- facing avoided information;
- choosing between plausible paths.

A Direction is not a task and not an immediate action. One Direction can produce many Smallest Human Actions over time.

Good Directions:

- Shape the demo story so a real person can understand why the app matters.
- Decide the first external push: demo/video, LinkedIn/outreach, or one real user conversation.
- Find a real person to try the app and learn whether it solves an actual problem.
- Choose which audience the project should serve first.

Bad Directions:

- Open Screen Studio and record the first 10 seconds.
- Write one LinkedIn sentence.
- Refactor a component.
- Research docs.

The first two are possible actions. The last two are agent tasks.

### 3.3 Smallest Human Action

A Smallest Human Action is the immediate action shown when the user asks for help starting.

It must be:

- concrete;
- directly executable by the user;
- startable within two minutes;
- tied to one Direction;
- not a plan;
- not a list;
- not something the agent can do instead.

Good:

```text
Write the first sentence of the demo voiceover. Stop there.
```

Bad:

```text
Clarify your positioning.
```

## 4. Interaction Model

There are three primary user-facing features.

### 4.1 Capture Directions

Triggered when the user describes messy project context, says they need to figure out where to go, or asks to capture directions.

The agent should:

1. Hydrate session context by reading the repo, especially `AGENTS.md`, `README*`, `docs/`, specs, plans, and product notes.
2. Read `.smallest-human-action/directions.json` if present, or migrate from `.one-human-move/moves.json` if that is the only state.
3. Use the current thread and repo context.
4. Separate Agent Tasks from Directions.
5. Ask one focused clarifying question only if necessary.
6. Write or update `.smallest-human-action/directions.json`.
7. Reply with a short summary of captured Directions.

Capture Directions must not output the smallest action. It should not collapse messy input into one or two tiny next steps. It preserves larger user-owned loops so future action requests have something meaningful to draw from.

Example response:

```text
I captured 3 Directions for this repo:

- Shape the demo story so a real person can understand why the app matters.
- Decide the first external push: demo/video, LinkedIn/outreach, or one real user conversation.
- Find a real person to try the app and learn whether it solves an actual problem.

I saved them to `.smallest-human-action/directions.json`.
```

### 4.2 Ask For Action

Triggered when the user asks for one action:

```text
give me an action
give me a smallest human action
我现在卡住了，给我一个 action
```

Adapters may treat old phrases such as `make move` as action requests, but the response should use Direction and Action language.

The agent should:

1. Hydrate session context.
2. Read `.smallest-human-action/directions.json`.
3. Consider the user's current energy and latest thread context.
4. Review prior action history and direction status.
5. Select one open or in-progress Direction.
6. Generate exactly one Smallest Human Action.
7. Record a `shown` event.

Response:

```text
Take this action:

Write the first sentence of the demo voiceover. Stop there.

Direction: Shape the demo story so a real person can understand why the app matters.
Why this direction: It helps both the landing page and outreach become less abstract.

Choose:
A. Done — I did it.
B. Too hard — make this action smaller.
C. Different direction — give me an action from another direction.
D. Not now — do not bring this direction back in this session.

Or reply in your own words with what happened, what you realized, or why this action is off.
```

### 4.3 Feedback Loop

Triggered when the user responds to an action with done, too hard, different direction, not now, or a natural-language update.

This is not just bookkeeping. Feedback should improve future suggestions. The skill should update `direction.actions[]`, direction notes, project context, and selection logic so the next action feels more precise.

Rules:

- Completed actions should not be repeated.
- Completed actions should make the Direction a little more progressed, even if the Direction is not resolved.
- Too-hard actions should shrink in size, ambiguity, emotional cost, or required setup.
- Skipped or not-now Directions should be deprioritized in the current session.
- User realizations should update project context or Direction notes before another action is generated.

Action suggestions belong under the Direction that generated them. `history[]` remains useful as a cross-Direction timeline, but `directions[].actions[]` is the canonical place for action text, status, and result.

## 5. Feedback Options

Visible replies:

```text
A. Done
B. Too hard
C. Different direction
D. Not now
```

- `A` / `done`: record progress. Do not mark the whole Direction resolved unless the underlying loop is resolved.
- `B` / `too hard`: keep the same Direction and make the action smaller.
- `C` / `different direction` / `skip`: record skipped and choose a different Direction if available.
- `D` / `not now`: avoid resurfacing this Direction in the current session.

Natural language updates should also work:

- "I did something else..." means record valid progress.
- "Actually I realized..." means update project context or Direction notes.
- "Make it more concrete" means rewrite the same action with fewer assumptions.
- "Wrong direction" or "wrong action" means ask one short repair question and update selection context.

## 6. Repo-Local State

State lives in the project repo:

```text
.smallest-human-action/directions.json
```

It is private local state by default and should be gitignored unless explicitly shared.

Older state may exist at:

```text
.one-human-move/moves.json
```

The MVP should migrate old state into the new path.

## 7. Schema

```json
{
  "version": 1,
  "project": {
    "name": "Smallest Human Action",
    "goal": "Create a repo-local skill that helps the user choose directions and take one smallest human action.",
    "context": [
      "The product is skill-first, not todo-app-first.",
      "Directions are larger user-owned loops. Actions are tiny executable steps."
    ],
    "agentBoundary": "The agent does tasks. The human chooses directions and takes actions."
  },
  "directions": [
    {
      "id": "direction_1",
      "title": "Shape the demo story so a real person can understand why the app matters.",
      "whyItMatters": "The demo reduces the user's own friction and gives future outreach something concrete.",
      "userOnlyReason": "Only the user can choose the story they actually believe and want to tell.",
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
          "text": "Write the first sentence of the demo voiceover. Stop there.",
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

`actionSeeds` is optional future action material. It is not shown automatically during capture.

## 8. Session Context Hydration

`directions.json` is not project understanding. Every session should refresh context before capturing Directions or generating an Action.

The agent should:

1. Inspect the repo with `rg --files` where available.
2. Read `AGENTS.md`, `README*`, `docs/`, specs, plans, and relevant product notes.
3. Read direction state.
4. Build working understanding from repo files and current conversation.

The user does not care whether context is written down. The guarantee is that the current session has loaded enough project context.

## 9. Empty State

If the user asks for an action before `directions.json` exists:

1. Do not immediately ask the user what the project is.
2. Inspect the repo first.
3. If enough context exists, create Directions and then return one Action.
4. If context is too thin, ask one focused question:

```text
I looked through the repo, but I cannot yet tell which direction requires your judgment.

What is the main decision or stuck point you are personally trying to move forward here?
```

## 10. Tone

The skill should sound calm, specific, direct, and non-motivational.

Good:

```text
Open the notes. Put a mark next to the sentence you most believe. Stop there.
```

Bad:

```text
Let's crush some progress and unlock your full potential.
```

## 11. MVP Scope

In scope:

- platform-agnostic Smallest Human Action protocol;
- Codex adapter;
- repo-local `.smallest-human-action/directions.json`;
- Capture Directions / Ask For Action / Feedback workflows;
- JSON validation and migration from `.one-human-move/moves.json`;
- clear distinction between Agent Task, Direction, and Smallest Human Action.

Out of scope:

- web app UI;
- cloud sync;
- calendar/reminders;
- team collaboration;
- habit streaks;
- automated project management.
