#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import re
from pathlib import Path


ROOT = Path("/Users/wycm/lycris_skill")
SOURCE = ROOT / "examples" / "wenwendexingfu-rational-analysis.md"
OUTPUT = ROOT / "examples" / "wenwendexingfu-rational-analysis.html"
RHYME_REPORT_JSON = ROOT / "examples" / "wenwendexingfu-rhyme-report.json"

RHYME_OVERVIEW_RE = re.compile(r"^## 全曲押韵总览\s*$", re.M)
RHYME_DIMENSION_RE = re.compile(r"^### (按.+)$", re.M)
SECTION_RE = re.compile(r"^## 第 (\d+) 段\s*$", re.M)
LINE_RE = re.compile(r"^## (L\d+)\s*$", re.M)


def parse_yaml_block(text: str) -> dict:
    result: dict = {}
    current_parent: str | None = None

    for raw in text.splitlines():
        line = raw.rstrip()
        if not line or line.strip() in {"```yaml", "```"}:
            continue

        if not line.startswith("  "):
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                result[key] = value
                current_parent = None
            else:
                result[key] = {}
                current_parent = key
        else:
            if current_parent is None:
                continue
            key, value = line.strip().split(":", 1)
            result[current_parent][key.strip()] = value.strip()

    return result


def extract_yaml_after(text: str, start_idx: int) -> tuple[dict, int]:
    code_start = text.find("```yaml", start_idx)
    if code_start == -1:
        raise ValueError("Missing yaml block")
    code_end = text.find("```", code_start + 7)
    if code_end == -1:
        raise ValueError("Unclosed yaml block")
    block = text[code_start : code_end + 3]
    parsed = parse_yaml_block(block)
    return parsed, code_end + 3


def build_data(md: str) -> dict:
    title = md.splitlines()[0].lstrip("# ").strip()
    intro = md.splitlines()[2].strip()
    song_rhyme: dict = {"summary": {}, "dimensions": []}
    sections = []

    section_matches = list(SECTION_RE.finditer(md))
    line_matches = list(LINE_RE.finditer(md))

    rhyme_match = RHYME_OVERVIEW_RE.search(md)
    if rhyme_match:
        rhyme_end = section_matches[0].start() if section_matches else len(md)
        summary_yaml, after_summary = extract_yaml_after(md, rhyme_match.end())
        dimensions_text = md[after_summary:rhyme_end]
        dimension_matches = list(RHYME_DIMENSION_RE.finditer(dimensions_text))
        dimensions = []
        for idx, match in enumerate(dimension_matches):
            body_start = match.end()
            body_end = dimension_matches[idx + 1].start() if idx + 1 < len(dimension_matches) else len(dimensions_text)
            body = " ".join(line.strip() for line in dimensions_text[body_start:body_end].strip().splitlines())
            dimensions.append({"name": match.group(1).strip(), "body": body})
        song_rhyme = {"summary": summary_yaml, "dimensions": dimensions}

    line_iter = iter(line_matches)
    pending = next(line_iter, None)

    for idx, match in enumerate(section_matches):
        section_number = match.group(1)
        section_start = match.end()
        section_end = section_matches[idx + 1].start() if idx + 1 < len(section_matches) else len(md)

        section_yaml, _ = extract_yaml_after(md, section_start)
        section_data = section_yaml.get("段级参数", {})

        lines = []
        while pending and pending.start() < section_end:
            line_id = pending.group(1)
            line_yaml, _ = extract_yaml_after(md, pending.end())
            lines.append(
                {
                    "id": line_id,
                    "single": line_yaml.get("单句本体参数", {}),
                    "context": line_yaml.get("上下文参数", {}),
                }
            )
            pending = next(line_iter, None)

        sections.append({"number": section_number, "meta": section_data, "lines": lines})

    return {"title": title, "intro": intro, "song_rhyme": song_rhyme, "sections": sections}


def load_rhyme_report() -> dict:
    if not RHYME_REPORT_JSON.exists():
        return {}
    return json.loads(RHYME_REPORT_JSON.read_text(encoding="utf-8"))


def clean_list(value: str) -> str:
    if not value:
        return "—"
    cleaned = value.strip().strip("[]").replace("'", "").replace('"', "")
    parts = [part.strip() for part in cleaned.split(",") if part.strip()]
    return " / ".join(parts) if parts else value


def yes_no(value: str) -> str:
    if value == "true":
        return "是"
    if value == "false":
        return "否"
    return value or "未标注"


def line_sentence_1(single: dict) -> str:
    phrase = single.get("核心短语", "") or single.get("原句", "")
    sentence_type = single.get("句式类型", "句子")
    semantic = single.get("语义类型", "表达")
    diction = single.get("措辞风格", "普通")
    return f"这句是一句{sentence_type}，核心落点是“{phrase}”，主要承担{semantic}，整体措辞偏向{diction}。"


def line_sentence_2(single: dict) -> str:
    topic = single.get("话题对象", "内容")
    imagery = yes_no(single.get("是否有意象", ""))
    imagery_type = single.get("意象类型", "无")
    rhetoric = single.get("修辞类型", "无")
    rhyme = single.get("韵脚", "—")
    cadence = single.get("节奏类型", "未标注")
    if imagery == "是":
        imagery_part = f"它会借助{imagery_type}这一类意象来承托“{topic}”"
    else:
        imagery_part = f"它主要直接处理“{topic}”这个对象"
    rhetoric_part = "修辞上没有刻意拐弯" if rhetoric in {"无", "无明显修辞"} else f"修辞上带有{rhetoric}的倾向"
    return f"{imagery_part}，{rhetoric_part}，句尾落在“{rhyme}”这一韵脚上，节奏感更接近{cadence}。"


def line_sentence_3(context: dict) -> str:
    prev_rel = context.get("与前句关系", "无")
    next_rel = context.get("与后句关系", "无")
    parts = []
    if prev_rel and prev_rel != "无":
        parts.append(f"放进上下文里，它先{prev_rel}")
    else:
        parts.append("放进上下文里，它前面没有承接对象")
    if next_rel and next_rel != "无":
        parts.append(f"再{next_rel}")
    else:
        parts.append("后面也不再继续展开")
    if yes_no(context.get("是否话题切换", "")) == "是":
        parts.append("这里同时发生了话题切换")
    if yes_no(context.get("是否逻辑转折", "")) == "是":
        parts.append("逻辑上也形成了转折")
    return "，".join(parts) + "。"


def line_sentence_4(context: dict) -> str:
    struct_role = context.get("结构作用", "未标注")
    theme_role = context.get("主题推进角色", "未标注")
    importance = context.get("主题重要度", "未标注")
    repeated = yes_no(context.get("是否重复句", ""))
    repeated_part = "它还是一条重复句" if repeated == "是" else "它不是重复句"
    return f"在本段中，这句承担的是“{struct_role}”；放到整首歌的主题推进里，它属于“{theme_role}”，主题重要度为“{importance}”，{repeated_part}。"


def section_lead(meta: dict) -> str:
    section_type = meta.get("段落角色", "") or meta.get("段落类型", "未标注段落")
    line_count = meta.get("段内句数", "0")
    task = meta.get("段落主题任务", "未标注")
    structure = meta.get("段内结构模式", "未标注")
    repeat = meta.get("段内重复模式", "未标注")
    rhyme = meta.get("段内押韵模式", "未标注")
    return (
        f"这一段属于{section_type}，一共 {line_count} 句，它最主要的任务是：{task}。"
        f" 从组织方式上看，这一段大致按“{structure}”来推进。"
        f" 在形式上，它的重复模式是“{repeat}”，押韵上可概括为：{rhyme}。"
    )


def chip_row(items: list[tuple[str, str]]) -> str:
    chips = []
    for key, value in items:
        if not value:
            continue
        chips.append(f'<span class="chip"><strong>{html.escape(key)}</strong>{html.escape(value)}</span>')
    return '<div class="chip-row">' + "".join(chips) + "</div>"


def percent(value: float | int | str) -> str:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number * 100:.1f}%"


def render_song_rhyme(song_rhyme: dict) -> str:
    summary = song_rhyme.get("summary", {})
    dimensions = song_rhyme.get("dimensions", [])
    if not summary and not dimensions:
        return ""

    summary_html = chip_row(
        [
            ("主要押韵组织", summary.get("主要押韵组织", "")),
            ("韵脚数量规律", summary.get("韵脚数量规律", "")),
            ("韵母严格程度", summary.get("韵母严格程度", "")),
            ("声调处理", summary.get("声调处理", "")),
            ("特殊技巧", summary.get("特殊技巧", "")),
            ("主要韵脚样例", summary.get("主要韵脚样例", "")),
        ]
    )
    dimension_cards = "".join(
        f"""
        <article class="rhyme-dimension-card">
          <h3>{html.escape(item["name"])}</h3>
          <p>{html.escape(item["body"])}</p>
        </article>
        """
        for item in dimensions
    )
    return f"""
    <section class="rhyme-overview">
      <div class="section-label">全曲押韵总览</div>
      <h2>全曲押韵总览</h2>
      {summary_html}
      <div class="rhyme-dimension-grid">
        {dimension_cards}
      </div>
    </section>
    """


def render_report_table(rows: list[dict]) -> str:
    body = "".join(
        f"""
        <tr>
          <td>{html.escape(row.get("label", ""))}</td>
          <td>{html.escape(str(row.get("total_lines", "")))}</td>
          <td>{html.escape(str(row.get("u_zone_count", "")))}</td>
          <td>{html.escape(percent(row.get("u_zone_density", "")))}</td>
          <td>{html.escape(str(row.get("entered_main_rhyme_count", "")))}</td>
          <td>{html.escape(percent(row.get("entered_main_rhyme_density", "")))}</td>
          <td>{html.escape(row.get("pattern", ""))}</td>
        </tr>
        """
        for row in rows
    )
    return f"""
    <div class="report-table-wrap">
      <table class="report-table">
        <thead>
          <tr>
            <th>区块</th>
            <th>总句数</th>
            <th>u 音句数</th>
            <th>u 音密度</th>
            <th>入主韵句数</th>
            <th>入主韵密度</th>
            <th>组织判断</th>
          </tr>
        </thead>
        <tbody>
          {body}
        </tbody>
      </table>
    </div>
    """


def render_macro_section(section: dict) -> str:
    notes = "".join(f"<li>{html.escape(note)}</li>" for note in section.get("notes", []))
    tail_rows = "".join(
        f"""
        <tr>
          <td>{html.escape(item.get("line_id", ""))}</td>
          <td>{html.escape(item.get("text", ""))}</td>
          <td>{html.escape(item.get("rhyme", ""))}</td>
          <td>{'是' if item.get("is_u_zone") else '否'}</td>
          <td>{'是' if item.get("in_main_rhyme") else '否'}</td>
          <td>{html.escape(item.get("stability", ""))}</td>
        </tr>
        """
        for item in section.get("line_tail_table", [])
    )
    stats = chip_row(
        [
            ("句子范围", " / ".join(section.get("line_ids", []))),
            ("u 音密度", percent(section.get("u_zone_density", ""))),
            ("入主韵密度", percent(section.get("entered_main_rhyme_density", ""))),
            ("角色", section.get("role", "")),
        ]
    )
    return f"""
    <article class="macro-card">
      <div class="section-label">Macro Section</div>
      <h3>{html.escape(section.get("label", ""))}</h3>
      <p class="macro-pattern">{html.escape(section.get("pattern", ""))}</p>
      {stats}
      <ul class="report-list">
        {notes}
      </ul>
      <div class="report-table-wrap compact">
        <table class="report-table compact">
          <thead>
            <tr>
              <th>句号</th>
              <th>原句</th>
              <th>韵脚</th>
              <th>u 音区</th>
              <th>入主韵</th>
              <th>稳定性</th>
            </tr>
          </thead>
          <tbody>
            {tail_rows}
          </tbody>
        </table>
      </div>
    </article>
    """


def render_device_cards(items: list[dict], caution: bool = False) -> str:
    cards = []
    for item in items:
        reason = item.get("note") or item.get("reason") or ""
        evidence = item.get("evidence", [])
        evidence_text = " / ".join(evidence) if isinstance(evidence, list) else str(evidence)
        cards.append(
            f"""
            <article class="device-card{' caution' if caution else ''}">
              <h4>{html.escape(item.get("name", ""))}</h4>
              <div class="device-status">{html.escape(item.get("status", ""))}</div>
              {'<p class="device-evidence"><strong>证据</strong>' + html.escape(evidence_text) + '</p>' if evidence_text else ''}
              <p>{html.escape(reason)}</p>
            </article>
            """
        )
    return "".join(cards)


def render_rhyme_report(report: dict) -> str:
    if not report:
        return ""

    summary = report.get("global_summary", {})
    summary_chips = chip_row(
        [
            ("主线", summary.get("core_progression", "")),
            ("主韵区", summary.get("main_rhyme_zone", "")),
            ("全曲 u 音密度", percent(summary.get("u_zone_density", ""))),
            ("全曲入主韵密度", percent(summary.get("entered_main_rhyme_density", ""))),
            ("押韵长度", summary.get("rhyme_length", "")),
            ("句尾福次数", str(summary.get("hook_fu_tail_count", ""))),
        ]
    )
    section_cards = "".join(render_macro_section(item) for item in report.get("macro_sections", []))
    confirmed = render_device_cards(report.get("confirmed_devices", []))
    cautionary = render_device_cards(report.get("cautionary_devices", []), caution=True)
    return f"""
    <section class="report-block">
      <div class="section-label">Rhyme Report</div>
      <h2>押韵专项报告</h2>
      <p class="report-intro">这一块直接挂接专项研究层，不再只展示参数字段。它同时保留宏观结构、密度变化、逐段尾韵证据，以及哪些手法可以确认、哪些只适合谨慎观察。</p>
      {summary_chips}
      {render_report_table(report.get("macro_sections", []))}
      <div class="macro-grid">
        {section_cards}
      </div>
      <div class="device-section">
        <h3>确认成立的手法</h3>
        <div class="device-grid">
          {confirmed}
        </div>
      </div>
      <div class="device-section">
        <h3>不建议硬判的标签</h3>
        <div class="device-grid">
          {cautionary}
        </div>
      </div>
    </section>
    """


def render_section(section: dict) -> str:
    meta = section["meta"]
    round_id = meta.get("轮次", "")
    round_name = meta.get("轮次名称", "")
    segment_name = meta.get("段名", "")
    segment_role = meta.get("段落角色", "") or meta.get("段落类型", "")
    segment_range = meta.get("句子范围", "")
    section_label = f"{round_id} · {round_name}".strip(" ·") or f"段落 {section['number']}"
    heading = f"第 {section['number']} 段"
    if segment_name:
        heading += f" · {segment_name}"
    segment_meta = " · ".join(part for part in [segment_role, segment_range] if part)
    line_rows = []

    for line in section["lines"]:
        single = line["single"]
        context = line["context"]
        chip_html = chip_row(
            [
                ("句式", single.get("句式类型", "")),
                ("关键词", clean_list(single.get("关键词", ""))),
                ("结构作用", context.get("结构作用", "")),
                ("主题推进", context.get("主题推进角色", "")),
                ("入主韵", yes_no(context.get("是否入本段主韵", ""))),
                ("押韵长度", context.get("单押/双押/多押情况", "")),
            ]
        )

        line_rows.append(
            f"""
            <div class="line-row">
              <div class="lyric-col">
                <div class="line-id">{html.escape(line["id"])}</div>
                <div class="lyric-text">{html.escape(single.get("原句", ""))}</div>
              </div>
              <div class="analysis-col">
                {chip_html}
                <div class="analysis-card">
                  <p>{html.escape(line_sentence_1(single))}</p>
                  <p>{html.escape(line_sentence_2(single))}</p>
                  <p>{html.escape(line_sentence_3(context))}</p>
                  <p class="emphasis">{html.escape(line_sentence_4(context))}</p>
                </div>
              </div>
            </div>
            """
        )

    return f"""
    <section class="section-block">
      <div class="section-header">
        <div class="section-label">{html.escape(section_label)}</div>
        <h2>{html.escape(heading)}</h2>
        {'<div class="segment-meta">' + html.escape(segment_meta) + '</div>' if segment_meta else ''}
      </div>
      <div class="section-intro">{html.escape(section_lead(meta))}</div>
      <div class="table-head">
        <div>原歌词</div>
        <div>分析</div>
      </div>
      {''.join(line_rows)}
    </section>
    """


def render_html(data: dict) -> str:
    rhyme_html = render_song_rhyme(data.get("song_rhyme", {}))
    sections_html = "".join(render_section(section) for section in data["sections"])
    report_html = render_rhyme_report(data.get("rhyme_report", {}))
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(data["title"])}</title>
  <style>
    :root {{
      --bg: #f5efe5;
      --paper: rgba(255, 251, 244, 0.94);
      --paper-2: rgba(247, 238, 223, 0.95);
      --ink: #1f1b16;
      --muted: #6f6355;
      --accent: #ab5e32;
      --accent-2: #2c5e59;
      --line: #d8c7ae;
      --shadow: 0 16px 42px rgba(73, 52, 31, 0.08);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "PingFang SC", "Hiragino Sans GB", "Noto Sans SC", sans-serif;
      color: var(--ink);
      background:
        radial-gradient(circle at top right, rgba(171, 94, 50, 0.12), transparent 24%),
        linear-gradient(180deg, #faf6ef 0%, #f1e8da 100%);
      line-height: 1.75;
    }}
    .page {{
      max-width: 1380px;
      margin: 0 auto;
      padding: 44px 24px 96px;
    }}
    .hero {{
      background: linear-gradient(135deg, rgba(255,251,244,0.98), rgba(246,236,219,0.93));
      border: 1px solid rgba(171, 94, 50, 0.18);
      border-radius: 30px;
      padding: 34px;
      box-shadow: var(--shadow);
      margin-bottom: 28px;
    }}
    .eyebrow {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      color: var(--accent);
      font-weight: 700;
      margin-bottom: 10px;
    }}
    h1 {{
      margin: 0 0 12px;
      font-size: clamp(30px, 5vw, 54px);
      line-height: 1.06;
      font-family: "STSong", "Songti SC", "Noto Serif SC", serif;
      font-weight: 700;
    }}
    .intro {{
      max-width: 940px;
      color: var(--muted);
      font-size: 16px;
      margin: 0;
    }}
    .legend {{
      margin-top: 18px;
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
    }}
    .legend span {{
      border-radius: 999px;
      padding: 8px 12px;
      background: rgba(171, 94, 50, 0.08);
      border: 1px solid rgba(171, 94, 50, 0.15);
      color: var(--accent);
      font-size: 13px;
      font-weight: 600;
    }}
    .section-block {{
      background: var(--paper);
      border: 1px solid var(--line);
      border-radius: 28px;
      box-shadow: var(--shadow);
      padding: 24px;
      margin-bottom: 28px;
    }}
    .report-block {{
      background: linear-gradient(135deg, rgba(255,251,244,0.98), rgba(243,233,216,0.94));
      border: 1px solid rgba(171, 94, 50, 0.18);
      border-radius: 30px;
      box-shadow: var(--shadow);
      padding: 28px;
      margin-bottom: 28px;
    }}
    .rhyme-overview {{
      background: linear-gradient(135deg, rgba(255,251,244,0.98), rgba(247,238,223,0.92));
      border: 1px solid rgba(44, 94, 89, 0.14);
      border-radius: 28px;
      box-shadow: var(--shadow);
      padding: 24px;
      margin-bottom: 28px;
    }}
    .section-label {{
      color: var(--accent-2);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      font-weight: 700;
      margin-bottom: 8px;
    }}
    .rhyme-dimension-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
      margin-top: 8px;
    }}
    .rhyme-dimension-card {{
      background: rgba(255,255,255,0.58);
      border: 1px solid rgba(111, 99, 85, 0.14);
      border-radius: 18px;
      padding: 16px 18px;
    }}
    .rhyme-dimension-card h3 {{
      margin: 0 0 10px;
      font-size: 18px;
      font-family: "STSong", "Songti SC", "Noto Serif SC", serif;
    }}
    .rhyme-dimension-card p {{
      margin: 0;
      font-size: 15px;
      color: var(--ink);
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 30px;
      font-family: "STSong", "Songti SC", "Noto Serif SC", serif;
    }}
    .section-intro {{
      background: var(--paper-2);
      border: 1px solid rgba(111, 99, 85, 0.12);
      border-radius: 18px;
      padding: 16px 18px;
      color: var(--ink);
      font-size: 15px;
      margin-bottom: 18px;
    }}
    .segment-meta {{
      color: var(--muted);
      font-size: 14px;
      font-weight: 600;
      margin: -4px 0 14px;
    }}
    .report-intro {{
      margin: 0 0 14px;
      color: var(--muted);
      font-size: 15px;
      max-width: 980px;
    }}
    .report-table-wrap {{
      overflow-x: auto;
      margin: 18px 0 22px;
      border: 1px solid rgba(111, 99, 85, 0.14);
      border-radius: 18px;
      background: rgba(255,255,255,0.45);
    }}
    .report-table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 860px;
      font-size: 14px;
    }}
    .report-table th,
    .report-table td {{
      padding: 12px 14px;
      border-bottom: 1px solid rgba(111, 99, 85, 0.12);
      text-align: left;
      vertical-align: top;
    }}
    .report-table th {{
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.14em;
      font-weight: 700;
      background: rgba(247,238,223,0.7);
    }}
    .report-table tbody tr:last-child td {{
      border-bottom: none;
    }}
    .report-table.compact {{
      min-width: 720px;
      font-size: 13px;
    }}
    .report-table-wrap.compact {{
      margin: 14px 0 0;
    }}
    .macro-grid {{
      display: grid;
      gap: 18px;
      margin-top: 8px;
    }}
    .macro-card {{
      background: rgba(255,255,255,0.52);
      border: 1px solid rgba(111, 99, 85, 0.14);
      border-radius: 22px;
      padding: 20px;
    }}
    .macro-card h3 {{
      margin: 0 0 8px;
      font-size: 24px;
      font-family: "STSong", "Songti SC", "Noto Serif SC", serif;
    }}
    .macro-pattern {{
      margin: 0 0 12px;
      color: var(--ink);
      font-size: 15px;
      font-weight: 600;
    }}
    .report-list {{
      margin: 0;
      padding-left: 20px;
      color: var(--ink);
      font-size: 14px;
    }}
    .report-list li + li {{
      margin-top: 6px;
    }}
    .device-section {{
      margin-top: 26px;
    }}
    .device-section h3 {{
      margin: 0 0 12px;
      font-size: 22px;
      font-family: "STSong", "Songti SC", "Noto Serif SC", serif;
    }}
    .device-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 16px;
    }}
    .device-card {{
      background: rgba(255,255,255,0.55);
      border: 1px solid rgba(44, 94, 89, 0.14);
      border-radius: 18px;
      padding: 16px 18px;
    }}
    .device-card.caution {{
      border-color: rgba(171, 94, 50, 0.18);
      background: rgba(255,248,241,0.72);
    }}
    .device-card h4 {{
      margin: 0 0 8px;
      font-size: 18px;
    }}
    .device-status {{
      display: inline-block;
      margin-bottom: 10px;
      padding: 4px 10px;
      border-radius: 999px;
      background: rgba(44, 94, 89, 0.08);
      color: var(--accent-2);
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}
    .device-card.caution .device-status {{
      background: rgba(171, 94, 50, 0.08);
      color: var(--accent);
    }}
    .device-card p {{
      margin: 0;
      font-size: 14px;
    }}
    .device-evidence {{
      margin: 0 0 8px;
      color: var(--muted);
    }}
    .table-head {{
      display: grid;
      grid-template-columns: minmax(220px, 0.78fr) minmax(0, 1.72fr);
      gap: 18px;
      padding: 0 4px 8px;
      color: var(--muted);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.18em;
      font-weight: 700;
    }}
    .line-row {{
      display: grid;
      grid-template-columns: minmax(220px, 0.78fr) minmax(0, 1.72fr);
      gap: 18px;
      padding: 18px 4px 22px;
      border-top: 1px dashed rgba(111, 99, 85, 0.24);
    }}
    .lyric-col {{
      align-self: start;
      position: sticky;
      top: 18px;
      background: linear-gradient(180deg, rgba(255,251,244,0.98), rgba(255,251,244,0.82));
      border: 1px solid rgba(171, 94, 50, 0.14);
      border-radius: 20px;
      padding: 16px;
    }}
    .line-id {{
      color: var(--accent);
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.16em;
      font-weight: 700;
      margin-bottom: 10px;
    }}
    .lyric-text {{
      font-family: "STSong", "Songti SC", "Noto Serif SC", serif;
      font-size: 24px;
      line-height: 1.4;
      white-space: pre-wrap;
    }}
    .analysis-col {{
      min-width: 0;
    }}
    .chip-row {{
      display: flex;
      gap: 10px;
      flex-wrap: wrap;
      margin-bottom: 12px;
    }}
    .chip {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      padding: 8px 12px;
      border-radius: 999px;
      background: rgba(44, 94, 89, 0.08);
      border: 1px solid rgba(44, 94, 89, 0.12);
      color: var(--accent-2);
      font-size: 13px;
      font-weight: 600;
    }}
    .analysis-card {{
      background: rgba(255,255,255,0.5);
      border: 1px solid rgba(111, 99, 85, 0.14);
      border-radius: 18px;
      padding: 16px 18px;
    }}
    .analysis-card p {{
      margin: 0 0 10px;
      font-size: 15px;
      color: var(--ink);
    }}
    .analysis-card p:last-child {{
      margin-bottom: 0;
    }}
    .analysis-card .emphasis {{
      color: var(--accent-2);
      font-weight: 700;
    }}
    @media (max-width: 980px) {{
      .rhyme-dimension-grid,
      .table-head, .line-row {{
        grid-template-columns: 1fr;
      }}
      .device-grid {{
        grid-template-columns: 1fr;
      }}
      .lyric-col {{
        position: static;
      }}
    }}
  </style>
</head>
<body>
  <main class="page">
    <section class="hero">
      <div class="eyebrow">Readable Analysis</div>
      <h1>{html.escape(data["title"])}</h1>
      <p class="intro">{html.escape(data["intro"])}</p>
      <div class="legend">
        <span>左栏：完整原歌词</span>
        <span>右栏：给人看的分析句</span>
        <span>每段先导语，再逐句分析</span>
      </div>
    </section>
    {rhyme_html}
    {report_html}
    {sections_html}
  </main>
</body>
</html>
"""


def main() -> None:
    md = SOURCE.read_text(encoding="utf-8")
    data = build_data(md)
    data["rhyme_report"] = load_rhyme_report()
    OUTPUT.write_text(render_html(data), encoding="utf-8")
    print(OUTPUT)


if __name__ == "__main__":
    main()
