# Prerequisites

## Step 1: Edit config.md

**First thing**: edit `references/config.md` with your local paths:
- `LYRICS_BASE` — where you want to clone the framework library
- `CODEX_BIN` — path to your codex-companion.mjs (find with `find ~/.claude/plugins/cache -name "codex-companion.mjs"`)

## Step 2: Clone the framework library

```bash
git clone https://github.com/chen-da-pang/lyrics-frameworks-skill $LYRICS_BASE
```

Replace `$LYRICS_BASE` with the path you set in config.md.

## Step 3: Install required tools

- **codex plugin** (for framework verification + lyrics generation):
  ```
  /plugin marketplace add openai/codex-plugin-cc
  /plugin install codex@openai-codex
  /reload-plugins
  ```
  Then authenticate: `!codex login`

- **gemini-cli** MCP (for parallel lyrics generation):
  Requires login: `!gemini auth login`
  If unavailable, skip — Codex will still run.

## Step 4: Python setup (for Sub-workflow A)

```bash
pip install -r ~/.claude/skills/lyrics-framework/requirements.txt
```
