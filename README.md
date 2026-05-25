# Smallest Human Action

Smallest Human Action is a portable agent workflow for helping a user take one project-aware, user-owned action when they are stuck, low-energy, foggy, avoidant, or unable to start.

Core principle:

```text
The agent does tasks.
The user chooses directions and takes actions.
```

This repository folder is the platform-agnostic source. Agent-specific integrations live under `adapters/`.

## What It Does

The workflow has three stages:

1. Capture Directions: turn messy user thoughts plus repo context into durable user-owned Directions.
2. Ask For Action: choose one Direction and generate one Smallest Human Action.
3. Feedback Loop: record each suggested action under its Direction so future suggestions get more precise.
4. Visualize Map: show all Directions and Actions with current status without opening JSON.

## Install For Codex

Copy the Codex adapter into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cp -R adapters/codex ~/.codex/skills/smallest-human-action
```

Then start a new Codex session in a repo and say something like:

```text
capture directions for this repo
```

## Layout

```text
smallest-human-action/
  protocol/
    smallest-human-action.md
    directions-schema.md
  scripts/
    directions_state.py
    update_directions.py
    validate_directions.py
  adapters/
    codex/
      SKILL.md
      agents/openai.yaml
      references/directions-schema.md
      scripts/
```

## Invocation

Natural language:

```text
capture directions for this repo
help me figure out which direction I need to move in
give me a smallest human action
give me an action
我现在卡住了，给我一个 action
show my direction map
visualize directions
看一下现在所有 direction 和 action 的状态
```

Older phrases such as `make move` can be treated as action requests by adapters, but the user-facing language should use Direction and Action.

## State

State lives in the current project repo:

```text
.smallest-human-action/directions.json
```

This is private local state by default and should be gitignored unless the user explicitly wants to share it.

Older `.one-human-move/moves.json` files may be migrated into the new state file.

## Notes

- The helper scripts use only the Python standard library.
- `.smallest-human-action/` should usually stay gitignored in project repos.
- The protocol is intended to be portable. Codex is the first adapter.
