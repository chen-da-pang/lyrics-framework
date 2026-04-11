from __future__ import annotations

from .models import LineAnnotation, LyricLine, SegmentBoundary
from .taxonomy import to_bool


RHYME_JIE_BY_VOWEL = {
    "ian": "言前辙",
    "ou": "由求辙",
    "ang": "江阳辙",
    "e": "梭波辙",
    "ie": "乜斜辙",
    "ong": "中东辙",
    "u": "姑苏辙",
}


def _segment_lookup(segments: list[SegmentBoundary]) -> dict[str, SegmentBoundary]:
    mapping: dict[str, SegmentBoundary] = {}
    for segment in segments:
        start = int(segment.line_start[1:])
        end = int(segment.line_end[1:])
        for index in range(start, end + 1):
            mapping[f"L{index:02d}"] = segment
    return mapping


def _semantic_role(
    line_id: str,
    text: str,
    segment_role: str,
    repeat_count: int,
    is_last_in_segment: bool,
) -> str:
    if line_id in {"L01", "L05", "L16", "L19"}:
        return "建立时间锚点"
    if text == "我要的幸福":
        return "抬升"
    if text == "我要稳稳的幸福":
        return "Hook" if repeat_count == 1 else "回返"
    if segment_role == "结尾" and line_id == "L39":
        return "收束"
    if segment_role == "扩展副歌":
        return "扩展确认"
    if is_last_in_segment:
        return "局部收束"
    return "铺垫状态"


def _line_type(text: str) -> str:
    if text == "我要稳稳的幸福":
        return "Hook宣言句"
    if text == "我要的幸福":
        return "导入短句"
    if len(text) <= 3:
        return "时间引子短句"
    if text.startswith("有一天"):
        return "时间起拍长句"
    return "叙述推进句"


def annotate_lines(
    lines: list[LyricLine],
    segments: list[SegmentBoundary],
    rhyme_audit: dict,
) -> list[LineAnnotation]:
    segment_by_line = _segment_lookup(segments)
    repeat_counter: dict[str, int] = {}
    audit_by_id = {item["line_id"]: item for item in rhyme_audit["lines"]}
    annotations: list[LineAnnotation] = []

    for line in lines:
        repeat_counter[line.text] = repeat_counter.get(line.text, 0) + 1
        segment = segment_by_line[line.line_id]
        audit_item = audit_by_id[line.line_id]
        rhyme = audit_item["rhyme"]
        is_last_in_segment = line.line_id == segment.line_end
        semantic_role = _semantic_role(
            line_id=line.line_id,
            text=line.text,
            segment_role=segment.role,
            repeat_count=repeat_counter[line.text],
            is_last_in_segment=is_last_in_segment,
        )
        annotations.append(
            LineAnnotation(
                line_id=line.line_id,
                segment_id=segment.segment_id,
                char_count=len(line.text.replace(" ", "")),
                line_type=_line_type(line.text),
                semantic_role=semantic_role,
                rhyme=rhyme,
                rhyme_jie=RHYME_JIE_BY_VOWEL.get(rhyme, "混辙"),
                rhyme_group=audit_item["rhyme_group"],
                in_main_rhyme=to_bool(audit_item["in_segment_main_rhyme"]),
                rhyme_length="单押",
                with_prev=to_bool(audit_item["with_prev"]),
                with_next=to_bool(audit_item["with_next"]),
                remote_rhyme=to_bool(audit_item["remote_rhyme"]),
                inner_rhyme=False,
                is_hook=line.text == "我要稳稳的幸福",
            )
        )

    return annotations
