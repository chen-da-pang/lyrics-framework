# User Configuration

Edit this file when installing on a new machine. All paths in this skill read from here.

## Required settings

```yaml
# Where the framework library lives on this machine
LYRICS_BASE: /Users/wycm/lycris_skill

# Codex companion script path (update if codex plugin version changes)
CODEX_BIN: node "/Users/wycm/.claude/plugins/cache/openai-codex/codex/1.0.3/scripts/codex-companion.mjs"
```

## Derived paths (do not edit — computed from LYRICS_BASE)

```
frameworks/        → $LYRICS_BASE/frameworks/
session-logs/      → $LYRICS_BASE/session-logs/
lyrics/            → $LYRICS_BASE/lyrics/
lyrics/TEMPLATE.md → $LYRICS_BASE/lyrics/TEMPLATE.md
frameworks/index.yaml → $LYRICS_BASE/frameworks/index.yaml
```

## How to find CODEX_BIN on a new machine

```bash
find ~/.claude/plugins/cache -name "codex-companion.mjs" 2>/dev/null
```

## GitHub (shared, no change needed)

Framework library: https://github.com/chen-da-pang/lyrics-frameworks-skill
