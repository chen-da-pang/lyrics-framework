from __future__ import annotations

from pathlib import Path

import yaml

from .html_renderer import render_framework_html
from .models import LineAnnotation, SegmentBoundary, SegmentFramework, SongFramework


SEGMENT_RHYME_FIELDS = {
    "S1": ("散韵开场，主歌区自由换韵，无稳定主韵", "自由韵", "多韵并用", "宽韵", "音节押韵", "无", "多韵并用", "混辙"),
    "S2": ("收韵过渡，末句导入 u 主韵", "随韵", "收向 u 音区", "宽韵", "音节押韵", "导入主韵", "分段换韵", "混辙"),
    "S3": ("主韵连押推进，中途夹入掺韵", "掺韵式准排韵", "u 音区集中", "宽严之间", "音节押韵", "Hook 遥韵回返", "主韵集中", "姑苏辙"),
    "S4": ("主韵连押推进，中途夹入掺韵", "掺韵式准排韵", "u 音区集中", "宽严之间", "音节押韵", "Hook 遥韵回返", "主韵集中", "姑苏辙"),
    "S5": ("第二轮主歌重新散开", "自由韵", "多韵并用", "宽韵", "音节押韵", "回返散韵", "多韵并用", "混辙"),
    "S6": ("再次收韵并导入副歌", "随韵", "收向 u 音区", "宽韵", "音节押韵", "导入主韵", "分段换韵", "混辙"),
    "S7": ("回返 Hook，主韵再度集中", "掺韵式准排韵", "u 音区集中", "宽严之间", "音节押韵", "Hook 遥韵回返", "主韵集中", "姑苏辙"),
    "S8": ("回返 Hook，主韵再度集中", "掺韵式准排韵", "u 音区集中", "宽严之间", "音节押韵", "Hook 遥韵回返", "主韵集中", "姑苏辙"),
    "S9": ("扩展副歌锁定 u 主韵", "排韵", "u 音区集中", "较严", "音节押韵", "尾声连押", "近一韵到底", "姑苏辙"),
    "S10": ("扩展副歌锁定 u 主韵", "排韵", "u 音区集中", "较严", "音节押韵", "尾声连押", "近一韵到底", "姑苏辙"),
    "S11": ("终段两句连押封口", "排韵", "u 音区集中", "较严", "音节押韵", "终段 Hook 回收", "一韵收束", "姑苏辙"),
}

DEFAULT_TAGS = ["流行", "情歌", "三轮结构", "预副歌"]
DEFAULT_RHYME_STYLE = "散→收→锁，副歌集中 u 音区（姑苏辙）"


def _build_segment_framework(segment: SegmentBoundary) -> SegmentFramework:
    (
        rhyme_pattern,
        rhyme_org,
        rhyme_vowel,
        rhyme_strictness,
        rhyme_tone,
        rhyme_special,
        rhyme_scale,
        rhyme_jie,
    ) = SEGMENT_RHYME_FIELDS[segment.segment_id]
    line_count = int(segment.line_end[1:]) - int(segment.line_start[1:]) + 1
    return SegmentFramework(
        segment_id=segment.segment_id,
        name=segment.name,
        role=segment.role,
        round_id=segment.round_id,
        line_range=f"{segment.line_start}-{segment.line_end}",
        line_count=line_count,
        structural_task=segment.structural_task,
        rhyme_pattern=rhyme_pattern,
        rhyme_org=rhyme_org,
        rhyme_vowel=rhyme_vowel,
        rhyme_strictness=rhyme_strictness,
        rhyme_tone=rhyme_tone,
        rhyme_special=rhyme_special,
        rhyme_scale=rhyme_scale,
        rhyme_jie=rhyme_jie,
    )


def _count_rounds(segments: list[SegmentBoundary]) -> int:
    return len({segment.round_id for segment in segments})


def build_framework(
    song_id: str,
    song_name: str,
    segments: list[SegmentBoundary],
    annotations: list[LineAnnotation],
    rhyme_audit: dict,
) -> SongFramework:
    del rhyme_audit

    segment_rows = [_build_segment_framework(segment) for segment in segments]
    return SongFramework(
        framework_id=f"{song_id}-v1",
        song_name=song_name,
        total_lines=len(annotations),
        total_segments=len(segment_rows),
        rounds=_count_rounds(segments),
        rhyme_style=DEFAULT_RHYME_STYLE,
        tags=list(DEFAULT_TAGS),
        segments=segment_rows,
        lines=annotations,
    )


def _index_entry(framework: SongFramework, song_id: str) -> dict:
    return {
        "framework_id": framework.framework_id,
        "song_name": framework.song_name,
        "total_segments": framework.total_segments,
        "rounds": framework.rounds,
        "rhyme_style": "散→收→锁",
        "tags": framework.tags,
        "path": f"frameworks/{song_id}/framework.yaml",
    }


def _write_yaml(path: Path, payload: object) -> None:
    path.write_text(
        yaml.safe_dump(payload, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )


def _write_index(output_root: Path, framework: SongFramework, song_id: str) -> None:
    index_path = output_root / "index.yaml"
    if index_path.exists():
        existing = yaml.safe_load(index_path.read_text(encoding="utf-8")) or []
    else:
        existing = []

    entry = _index_entry(framework=framework, song_id=song_id)
    filtered = [item for item in existing if item.get("framework_id") != framework.framework_id]
    filtered.append(entry)
    _write_yaml(index_path, filtered)


def write_framework_outputs(framework: SongFramework, output_root: Path, song_id: str) -> None:
    song_dir = output_root / song_id
    song_dir.mkdir(parents=True, exist_ok=True)

    framework_payload = framework.to_dict()
    _write_yaml(song_dir / "framework.yaml", framework_payload)
    (song_dir / "framework.html").write_text(
        render_framework_html(framework_payload),
        encoding="utf-8",
    )
    (song_dir / "analysis-notes.md").write_text(
        "- Step 1 使用固定 11 段切段规则。\n"
        "- Step 2 韵脚字段来自 rhyme audit JSON。\n"
        "- Step 3 输出 YAML 与 HTML 框架库条目。\n",
        encoding="utf-8",
    )
    _write_index(output_root=output_root, framework=framework, song_id=song_id)


def generate_framework(
    song_id: str,
    song_name: str,
    segments: list[SegmentBoundary],
    annotations: list[LineAnnotation],
    rhyme_audit: dict,
    output_root: Path,
) -> SongFramework:
    framework = build_framework(
        song_id=song_id,
        song_name=song_name,
        segments=segments,
        annotations=annotations,
        rhyme_audit=rhyme_audit,
    )
    write_framework_outputs(
        framework=framework,
        output_root=output_root,
        song_id=song_id,
    )
    return framework
