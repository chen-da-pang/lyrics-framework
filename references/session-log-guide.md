# Session Log Guide

## Create at session start

```bash
mkdir -p /Users/wycm/lycris_skill/session-logs
SESSION_LOG="/Users/wycm/lycris_skill/session-logs/$(date +%Y-%m-%d-%H%M%S).md"
```

Write initial content with actual datetime replacing `YYYY-MM-DD HH:MM`. Store path in `$SESSION_LOG` — reuse throughout the session.

Initial file content:
```
---
date: YYYY-MM-DD HH:MM
---

# Lyrics Framework Session
```

## Append template

Each entry format:
```
## [HH:MM] User
{用户说的话}

## [HH:MM] Assistant
{你说的话、分析结果、输出的歌词、修改记录等}
```

## When to append

- 用户的每一条输入
- 每次分析结果（分段、押韵、框架生成）
- 填词输出（完整歌词）
- 用户提出修改意见时
- 修改完成后

## Modification record format

```
## [HH:MM] 修改记录
**用户反馈**：{反馈内容}
**修改前**：{原句}
**修改后**：{新句}
```

## Async writing

Use a background subagent to append to the log — do not block the main workflow waiting for log writes.
