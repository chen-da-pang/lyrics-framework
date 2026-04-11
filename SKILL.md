---
name: lyrics-framework
description: "Analyze Chinese pop lyrics to extract reusable structural frameworks, then fill new lyrics using the framework with four parallel AI models (Claude, Codex, Gemini, Qwen). Use when the user provides song lyrics to analyze, wants to fill lyrics using an existing framework, or provides both lyrics and a theme/mood for end-to-end analysis + fill. Triggers on: 分析这首歌词, 提取歌词框架, 用框架填词, 帮我写歌词, 生成suno提示词, or any request involving Chinese song lyrics analysis or creation."
---

## Prerequisites

### Required skills & tools

- **codex:rescue** plugin (for framework verification + lyrics review):
  ```
  /plugin marketplace add openai/codex-plugin-cc
  /plugin install codex@openai-codex
  /reload-plugins
  ```
  Then authenticate: `!codex login`

- **qwen-code** skill (for parallel lyrics generation):
  Install via skillsmp or manually. Requires `qwen` CLI authenticated: `!qwen login`

- **gemini-cli** MCP (for parallel lyrics generation):
  Requires login: `!gemini auth login`
  If unavailable, skip — Claude + Codex + Qwen will still run.

### Python setup (for Sub-workflow A framework file generation)

```bash
pip install -r ~/.claude/skills/lyrics-framework/requirements.txt
```

The Python package is bundled at `~/.claude/skills/lyrics-framework/scripts/lyrics_framework_extraction/`.

### Framework library

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

---

## Overview

Two sub-workflows, often chained:

- **Sub-workflow A** — Lyrics → Framework: analyze a song, extract a reusable structural skeleton, store in the framework library
- **Sub-workflow B** — Framework → Lyrics: fill new lyrics using a framework with four parallel AI models, review, output Suno format

**User gives lyrics only** → run A  
**User gives theme/mood only** → ask which framework from `index.yaml`, then run B  
**User gives lyrics + theme/mood** → run A then B in sequence

## AI Tools

- **Codex** — via `codex:rescue` skill. Use `Skill("codex:rescue", args="<prompt>")`. If unavailable, skip and note it in the response; proceed with remaining models.
- **Qwen** — via `qwen-code` skill. Use `Skill("qwen-code", args="<prompt>")`. If unavailable (auth expired), skip and note it; remind user to run `qwen login`.
- **Gemini** — via `gemini-cli` MCP server (tool: `mcp__gemini-cli__ask-gemini`). If unavailable, skip and note it; remind user to run `gemini auth login`.
- **Claude** — self, write directly in response. Always runs regardless of other tool availability.

---

## Sub-workflow A: Lyrics → Framework

### Step 1: Segment

Number each line `L01`, `L02`… if not already numbered. Apply rules in `references/segmentation-rules.md`:
- Find round boundaries first (strong signals), then segment roles within each round
- Output: `segment_id → line_range → role → round`

Then use `codex:rescue` skill to independently verify the segment map:
```
Skill("codex:rescue", args="按照分段规则，独立验证这份歌词的分段结果是否正确，列出你认为有问题的地方和理由。规则：~/.claude/skills/lyrics-framework/references/segmentation-rules.md [歌词和分段结果]")
```

### Step 2: Annotate each line

For each line determine:
- `char_count`: character count (no spaces)
- `line_type`: 时间引子短句 / Hook宣言句 / 叙述推进句 / 导入短句 / etc.
- `semantic_role`: one of the 13 tags in `references/semantic-roles.md`
- Rhyme fields: analyze per `references/rhyme-taxonomy.md`

### Step 3: Deep rhyme analysis

Using `references/rhyme-taxonomy.md`, check all six dimensions for hidden techniques (inner rhyme, head rhyme chains, compound-syllable rhyme words, cross-辙 near-rhyme). Update rhyme audit with `inner_rhyme`, `head_rhyme`, `rhyme_length` fields.

Then use `codex:rescue` skill to independently verify the rhyme analysis:
```
Skill("codex:rescue", args="按照六维押韵体系，独立验证这份押韵分析是否有遗漏或误判，重点检查内韵、头韵链、叠韵词。规则：~/.claude/skills/lyrics-framework/references/rhyme-taxonomy.md [押韵分析内容]")
```

### Step 4: Generate framework files

Output to `/Users/wycm/lycris_skill/frameworks/{song_id}/`:
- `framework.yaml` — three-layer structure (meta / segments / lines)
- `framework-fillable.md` — fill template (see format rules below)
- Update `/Users/wycm/lycris_skill/frameworks/index.yaml`

**framework-fillable.md format rules:**
- Each line: `LXX [Nchar] [押韵标注]`
- 押韵标注: `[押主韵]` / `[散韵]` / `[掺韵]` / `[导入主韵]`
- For S5/S6 (second-round verse/pre-chorus): state explicitly they are compressed returns of S1/S2 with line-by-line mapping (e.g. "L16 = L01+L02 合并压缩，L17 ≈ L03，L18 ≈ L04")
- Do NOT bind to a specific rhyme vowel — describe rhyme logic only
- Extract original song's main rhyme vowel from `rhyme_style` in `framework.yaml` — used in Sub-workflow B

**After generating framework files — commit & push to GitHub:**
```bash
cd /Users/wycm/lycris_skill
git add frameworks/{song_id}/ frameworks/index.yaml
git commit -m "Add framework: {song_name}"
git push
```

---

## Sub-workflow B: Framework → Lyrics

### Step 1: Build fill prompt

Read `framework-fillable.md`. Read `framework.yaml` → extract original main rhyme vowel from `rhyme_style`.

Hard constraints to include in every fill prompt:
```
- 不能使用 [原曲主韵] 作为主韵，自选其他韵
- 严格遵守每句字数，不能多也不能少
- Hook句在全曲所有标注「← Hook句」的位置完全重复，一字不差
- [押主韵]的句子句尾必须押选定的主韵
- [掺韵]的句子故意不押主韵
- S5/S6必须是S1/S2的压缩回返，不能重新创作新内容
- 只输出歌词，每句标注行号，不要输出其他内容
```

Add user's theme and mood.

### Step 2: Parallel fill — four AI models

Run all four simultaneously:

**Claude (self):**
- Use the same fill prompt
- Choose a writing style that best fits the user's story and mood — do not default to a fixed style, read the theme and decide
- Write directly in the response, do not delegate

**Codex** (via `codex:rescue` skill):
```
Skill("codex:rescue", args="<fill prompt>")
```

**Gemini** (via `gemini-cli` MCP tool `gemini_ask`):
- Same fill prompt + style note: "偏意象化、诗意风格"
- If Gemini is unavailable (not logged in), skip and note it

**Qwen** (via `qwen-code` skill):
```bash
qwen "<fill prompt>"
```

### Step 3: Review with Codex

Pass all completed lyrics to `codex:rescue` skill for line-by-line review using the template in `references/review-prompt.md`:

```
Skill("codex:rescue", args="<review prompt with all lyrics>")
```

Review checks (every line individually — no range shortcuts like "L22-L39 all correct"):
1. Char count per line
2. Rhyme correctness per line
3. Hook consistency across all Hook positions
4. S5/S6 return quality
5. Theme/mood fit

Save output as `lyrics-comparison.md` in the framework folder.

### Step 4: Suno output

Convert best-scoring version:
- Segment tags: `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`, `[Verse 2]`, `[Bridge]`, `[Outro]`
- Repeated chorus: use `[Chorus]` tag without repeating lyrics
- Suno style prompt: English, ≤50 words, covering genre / mood / instruments / vocal style
- Label the source clearly: "本版本由 [Claude / Codex / Gemini / Qwen] 创作"

After outputting, ask:

> 这版词满意吗？如果想看看其他 AI 的版本，可以告诉我——Claude、Codex、Gemini、Qwen 各写了一版。

---

## Framework library

- **Local path**: `/Users/wycm/lycris_skill/frameworks/`
- **GitHub**: https://github.com/chen-da-pang/lyrics-frameworks-skill
- **Index**: `/Users/wycm/lycris_skill/frameworks/index.yaml`
- **Python package**: `~/.claude/skills/lyrics-framework/scripts/lyrics_framework_extraction/`
- **Render script**: `~/.claude/skills/lyrics-framework/scripts/render_lyrics_analysis_html.py`

## References

- `references/segmentation-rules.md` — segmentation signal rules
- `references/semantic-roles.md` — 13 canonical semantic role tags
- `references/rhyme-taxonomy.md` — six-dimension rhyme system + 十三辙
- `references/review-prompt.md` — review prompt template
