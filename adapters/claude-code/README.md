# Claude Code Adapter

Install this adapter as a Claude Code skill:

```bash
mkdir -p ~/.claude/skills
cp -R adapters/claude-code ~/.claude/skills/smallest-human-action
```

Restart Claude Code or start a new session in a project repo, then try:

```text
capture directions for this repo
```

Project-local state is written to:

```text
.smallest-human-action/directions.json
```

Add `.smallest-human-action/` to the project repo's `.gitignore` unless you intentionally want to share that state.
