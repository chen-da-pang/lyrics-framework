from __future__ import annotations

import html


def _render_structure_items(segments: list[dict]) -> str:
    return "".join(
        (
            "<li>"
            f"{html.escape(item['segment_id'])} · "
            f"{html.escape(item['name'])} · "
            f"{html.escape(item['line_range'])}"
            "</li>"
        )
        for item in segments
    )


def _render_segment_cards(segments: list[dict]) -> str:
    return "".join(
        f"""
        <article class="segment-card">
          <h3>{html.escape(item['name'])}</h3>
          <p>{html.escape(item['role'])} · {html.escape(item['round_id'])} · {html.escape(item['line_range'])}</p>
          <p>结构任务：{html.escape(item['structural_task'])}</p>
          <p>押韵模式：{html.escape(item['rhyme_pattern'])}</p>
          <p>韵组织：{html.escape(item['rhyme_org'])} · {html.escape(item['rhyme_jie'])}</p>
        </article>
        """
        for item in segments
    )


def _render_line_cards(lines: list[dict]) -> str:
    return "".join(
        f"""
        <article class="line-card {'main-rhyme' if item['in_main_rhyme'] else 'loose-rhyme'}">
          <h3>{html.escape(item['line_id'])}</h3>
          <p>句式：{html.escape(item['line_type'])}</p>
          <p>语义角色：{html.escape(item['semantic_role'])}</p>
          <p>字数：{item['char_count']}</p>
          <p>押韵：{html.escape(item['rhyme'])} / {html.escape(item['rhyme_group'])}</p>
        </article>
        """
        for item in lines
    )


def render_framework_html(framework: dict) -> str:
    structure_items = _render_structure_items(framework["segments"])
    segment_cards = _render_segment_cards(framework["segments"])
    line_cards = _render_line_cards(framework["lines"])

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <title>{html.escape(framework['song_name'])} framework</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #1f2937;
      --muted: #475569;
      --panel: #ffffff;
      --panel-alt: #f8fafc;
      --line: #d1d5db;
      --accent: #0f766e;
      --accent-soft: #ccfbf1;
      --bg: linear-gradient(180deg, #f7f4ed 0%, #eef6ff 100%);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: "PingFang SC", "Noto Sans SC", sans-serif;
      color: var(--ink);
      background: var(--bg);
    }}
    main {{
      max-width: 1120px;
      margin: 0 auto;
      padding: 40px 20px 64px;
    }}
    header {{
      background: rgba(255, 255, 255, 0.82);
      backdrop-filter: blur(14px);
      border: 1px solid rgba(209, 213, 219, 0.8);
      border-radius: 24px;
      padding: 28px;
      box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
    }}
    h1, h2, h3 {{
      margin: 0;
    }}
    h1 {{
      font-size: 2.2rem;
      margin-bottom: 10px;
    }}
    h2 {{
      font-size: 1.3rem;
      margin-bottom: 16px;
    }}
    section {{
      margin-top: 24px;
      background: rgba(255, 255, 255, 0.9);
      border: 1px solid rgba(209, 213, 219, 0.85);
      border-radius: 24px;
      padding: 24px;
      box-shadow: 0 14px 36px rgba(15, 23, 42, 0.05);
    }}
    ul {{
      margin: 0;
      padding-left: 20px;
      color: var(--muted);
    }}
    .meta {{
      color: var(--muted);
      line-height: 1.7;
    }}
    .grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
      gap: 16px;
    }}
    .segment-card, .line-card {{
      border-radius: 20px;
      padding: 18px;
      border: 1px solid var(--line);
      background: var(--panel);
    }}
    .segment-card {{
      background: linear-gradient(180deg, #ffffff 0%, #f8fbff 100%);
    }}
    .line-card {{
      background: var(--panel-alt);
    }}
    .line-card.main-rhyme {{
      border-color: rgba(15, 118, 110, 0.4);
      background: linear-gradient(180deg, var(--accent-soft) 0%, #f0fdfa 100%);
    }}
    p {{
      margin: 10px 0 0;
      line-height: 1.6;
      color: var(--muted);
    }}
    strong {{
      color: var(--accent);
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>{html.escape(framework['song_name'])} 框架</h1>
      <p class="meta">{html.escape(framework['framework_id'])} · 共 {framework['total_segments']} 段 · {framework['total_lines']} 句 · {framework['rounds']} 轮</p>
      <p class="meta">韵律风格：{html.escape(framework['rhyme_style'])}</p>
    </header>
    <section>
      <h2>全曲结构概览</h2>
      <ul>{structure_items}</ul>
    </section>
    <section>
      <h2>段级参数</h2>
      <div class="grid">{segment_cards}</div>
    </section>
    <section>
      <h2>句级卡片</h2>
      <div class="grid">{line_cards}</div>
    </section>
    <section>
      <h2>押韵密度</h2>
      <p><strong>高亮卡片</strong>表示进入当前段主韵的句子；其余卡片表示散韵、掺韵或过渡句。</p>
    </section>
  </main>
</body>
</html>"""
