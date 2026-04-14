# Prerequisites

## Required skills & tools

- **codex:rescue** plugin (for framework verification + lyrics review):
  ```
  /plugin marketplace add openai/codex-plugin-cc
  /plugin install codex@openai-codex
  /reload-plugins
  ```
  Then authenticate: `!codex login`

- **gemini-cli** MCP (for parallel lyrics generation):
  Requires login: `!gemini auth login`
  If unavailable, skip — Codex will still run.

## Python setup (for Sub-workflow A framework file generation)

```bash
pip install -r ~/.claude/skills/lyrics-framework/requirements.txt
```

The Python package is bundled at `~/.claude/skills/lyrics-framework/scripts/lyrics_framework_extraction/`.

## Framework library

- **Local path**: `/Users/wycm/lycris_skill/frameworks/`
- **GitHub**: https://github.com/chen-da-pang/lyrics-frameworks-skill
- **Clone on new machine**:
  ```bash
  git clone https://github.com/chen-da-pang/lyrics-frameworks-skill /Users/wycm/lycris_skill
  ```
- **index.yaml**: `/Users/wycm/lycris_skill/frameworks/index.yaml` — lists all available frameworks. Create if missing:
  ```bash
  echo "[]" > /Users/wycm/lycris_skill/frameworks/index.yaml
  ```
