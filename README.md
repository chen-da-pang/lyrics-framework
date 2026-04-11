# lyrics-framework

A Claude Code skill that extracts reusable structural frameworks from Chinese pop songs, then fills new lyrics using four parallel AI models.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## What it does

**Sub-workflow A — Lyrics → Framework**: Give it a song's lyrics. It segments the song, annotates each line (char count, rhyme, semantic role), and saves a reusable structural skeleton to the framework library.

**Sub-workflow B — Framework → Lyrics**: Give it a theme and pick a framework. Four AI models (Claude, Codex, Gemini, Qwen) write lyrics in parallel. A two-layer review — framework compliance check + anonymous content quality scoring — picks the best version and outputs it in Suno format.

## Prerequisites

**Claude Code skills and tools:**
```
# codex:rescue plugin
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins

# Authenticate Codex
!codex login

# Authenticate Qwen (qwen-code skill required)
!qwen login

# Authenticate Gemini
!gemini auth login
```

**Python** (for Sub-workflow A framework generation):
```bash
pip install -r requirements.txt  # PyYAML==6.0.2
```

**Framework library** (clone to local path):
```bash
git clone https://github.com/chen-da-pang/lyrics-frameworks-skill /Users/wycm/lycris_skill
```

## Install the skill

```bash
# Clone to your Claude Code skills directory
git clone https://github.com/chen-da-pang/lyrics-framework ~/.claude/skills/lyrics-framework
```

Claude Code auto-discovers skills in `~/.claude/skills/`. The skill triggers on: `分析这首歌词`, `用框架填词`, `帮我写歌词`, `生成suno提示词`, or any request involving Chinese song lyrics.

## Usage

**Analyze a song:**
> 分析这首歌词，提取框架：[paste lyrics]

**Fill lyrics with a theme:**
> 用「从不主动示弱」框架写一首歌，主题是：两个人都知道感情撑不住了，但谁都不肯先说

**End-to-end (analyze + fill):**
> 分析这首歌词，然后用这个框架写一首关于[theme]的歌

## Framework library

8 frameworks available: [lyrics-frameworks-skill](https://github.com/chen-da-pang/lyrics-frameworks-skill)

Covers standard 3-round pop, dual-chorus, rap structure, Cantonese pop, inverted structure, and more.

## Review process

Lyrics go through two independent review layers:

1. **Framework compliance** (Codex) — char count per line, rhyme correctness, Hook consistency, return quality
2. **Content quality** (anonymous parallel subagents) — naturalness, imagery coherence, emotional impact, originality, theme fit

Versions are labeled A/B/C during content review to prevent model bias.

## License

MIT
