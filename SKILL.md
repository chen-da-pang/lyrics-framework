---
name: lyrics-framework
description: "Analyze Chinese pop lyrics to extract reusable structural frameworks, then fill new lyrics using the framework with two parallel AI models (Codex + Gemini). Use when the user provides song lyrics to analyze, wants to fill lyrics using an existing framework, or provides both lyrics and a theme/mood for end-to-end analysis + fill. Triggers on: 分析这首歌词, 提取歌词框架, 用框架填词, 帮我写歌词, 生成suno提示词."
---

> **Setup**: See `references/prerequisites.md` for installation instructions (codex:rescue, gemini-cli, Python, framework library clone).

## Hard Rules

- **歌名/歌手**：用户没有提供就留空（`song_name: unknown`，`artist: unknown`），绝对不能虚构或猜测
- **AI 工具失败**：Codex 或 Gemini 调用失败，直接报告失败原因，不能自己补写替代版本

## Configuration

```yaml
review_enabled: false   # Set to true to enable review steps (A: post-segmentation + post-rhyme; B: two-layer review + Suno audit fields)
```

## Session Log

At the start of every invocation, create a timestamped session log in `/Users/wycm/lycris_skill/session-logs/`. See `references/session-log-guide.md` for the template and append rules. Use a background subagent for all log writes — never block the main workflow.

## Overview

Two sub-workflows, often chained:

- **Sub-workflow A** — Lyrics → Framework: analyze a song, extract a reusable structural skeleton, store in the framework library
- **Sub-workflow B** — Framework → Lyrics: fill new lyrics using a framework with two parallel AI models (Codex + Gemini), review, output Suno format

**User gives lyrics only** → run A  
**User gives theme/mood only** → ask which framework from `index.yaml`, then run B  
**User gives lyrics + theme/mood** → run A then B in sequence

## AI Tools

Define once and reuse:
```bash
CODEX='node "/Users/wycm/.claude/plugins/cache/openai-codex/codex/1.0.3/scripts/codex-companion.mjs"'
```

- **Codex** — `$CODEX task --background --write`. Launch in background, get job-id immediately, poll with `$CODEX status`, fetch with `$CODEX result`. Do NOT use `codex:rescue` skill for fill tasks (it blocks).
- **Gemini** — `mcp__gemini-cli__ask-gemini`. Style note: "偏意象化、诗意风格". If unavailable (429 or not logged in), report error and proceed with Codex only.

---

## Sub-workflow A: Lyrics → Framework

### Step 1: Segment

Number each line `L01`, `L02`… if not already numbered. Apply rules in `references/segmentation-rules.md`:
- Find round boundaries first (strong signals), then segment roles within each round
- Output: `segment_id → line_range → role → round`

Then use `codex:rescue` skill to independently verify the segment map:

> **Skip if `review_enabled: false`**

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

> **Skip if `review_enabled: false`**

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

Include the hard constraints from `references/fill-constraints.md` verbatim in every fill prompt, plus user's theme and mood.

### Step 2: Parallel fill — two AI models

> **PARALLEL**: Issue the Codex background launch (2a) and the Gemini call (2b) in the same response turn — do not wait for either before issuing the other.

**Step 2a — Launch Codex in background:**

Write the fill prompt to `/tmp/lyrics_fill_prompt.txt` first, then invoke via Python to avoid shell quoting issues:
```bash
# Write prompt to file first (avoids shell special-char expansion)
cat > /tmp/lyrics_fill_prompt.txt << 'PROMPT_EOF'
<fill prompt content here>
PROMPT_EOF

# Launch via Python — safe for any prompt content
JOB_ID=$(python3 -c "
import subprocess
prompt = open('/tmp/lyrics_fill_prompt.txt').read()
r = subprocess.run(
    ['node', '/Users/wycm/.claude/plugins/cache/openai-codex/codex/1.0.3/scripts/codex-companion.mjs',
     'task', '--background', '--write', prompt],
    capture_output=True, text=True)
print(r.stdout)
" 2>&1 | grep -o 'task-[a-z0-9-]*')
echo "Codex job: $JOB_ID"
```

**Step 2b — Call Gemini immediately (same turn as 2a):**
```
mcp__gemini-cli__ask-gemini("<fill prompt> 偏意象化、诗意风格")
```

**Step 2c — After Gemini returns, poll Codex until done:**
```bash
$CODEX status $JOB_ID   # repeat until phase: done
$CODEX result $JOB_ID   # fetch lyrics
```

If Codex fails or times out (>5 min), report the error and proceed with Gemini version only.  
If Gemini fails (429 or unavailable), report the error and proceed with Codex version only.

### Step 3: Two-layer review

> **Skip this step if `review_enabled: false`**. Go directly to Step 4.

**Layer 1 — Framework compliance (Codex):**

Pass all completed lyrics to `codex:rescue` skill for line-by-line review using the template in `references/review-prompt.md`. Checks: char count per line, rhyme correctness, Hook consistency, S5/S6 return quality.

**Layer 2 — Content quality (parallel anonymous subagents):**

Launch one subagent per version simultaneously. Label versions A/B/C — do NOT reveal which AI wrote which. Each rates independently on: 语感流畅度 / 意象统一性 / 情绪感染力 / 原创性 / 主题契合度.

Combine both layers to determine the recommended version. Save full output as `lyrics-comparison.md` in the framework folder.

### Step 4: Suno output

Save both versions to `/Users/wycm/lycris_skill/lyrics/story-{NN}-{image}.md` using the template at `/Users/wycm/lycris_skill/lyrics/TEMPLATE.md`. Each version includes:
- Suno style prompt (English, ≤50 words: genre / mood / instruments / vocal style / BPM)
- Full lyrics with segment tags: `[Verse 1]`, `[Pre-Chorus]`, `[Chorus]`, `[Verse 2]`, `[Bridge]`, `[Outro]`
- Source label: "本版本由 [Codex / Gemini] 创作"
- 审核意见 and 综合推荐: **only include if `review_enabled: true`**

After outputting, ask: 这两版词你更喜欢哪个？

---

## 修改记录工作流

当用户对已输出的歌词提出任何修改意见时，执行以下流程：

### Step 1: 记录并修改

按用户要求修改歌词，同时在对应 `lyrics/story-{NN}-{image}.md` 文件末尾的 `## 修改记录` 区块追加：

```markdown
### v{N} ({YYYY-MM-DD})

**用户反馈**：{用户原话或归纳}
**修改类型**：{Hook句 / 意象 / 字数 / 押韵 / 情绪 / 结构 / 其他}
**修改位置**：{段落 + 行}
**修改前**：{原句}
**修改后**：{新句}
```

### Step 2: 追加到 session log（background subagent）

See `references/session-log-guide.md` for the modification record format.

---

## Framework library

- **Local path**: `/Users/wycm/lycris_skill/frameworks/`
- **GitHub**: https://github.com/chen-da-pang/lyrics-frameworks-skill
- **Index**: `/Users/wycm/lycris_skill/frameworks/index.yaml`
- **Lyrics output**: `/Users/wycm/lycris_skill/lyrics/` — story-{NN}-{image}.md (not tracked by git)
- **Lyrics template**: `/Users/wycm/lycris_skill/lyrics/TEMPLATE.md`

## References

- `references/prerequisites.md` — setup instructions (tools, Python, framework library)
- `references/segmentation-rules.md` — segmentation signal rules
- `references/semantic-roles.md` — 13 canonical semantic role tags
- `references/rhyme-taxonomy.md` — six-dimension rhyme system + 十三辙
- `references/fill-constraints.md` — hard constraints for every fill prompt
- `references/review-prompt.md` — Codex review prompt template
- `references/session-log-guide.md` — session log template and append rules

