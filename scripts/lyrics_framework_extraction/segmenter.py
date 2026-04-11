from __future__ import annotations

from .models import LyricLine, SegmentBoundary


STRUCTURAL_TASKS = {
    "S1": "建立起点，铺垫状态",
    "S2": "抬升并导入主韵",
    "S3": "首次主题宣言并锁定 Hook",
    "S4": "扩写副歌命题并保持主韵",
    "S5": "回返主歌并重启散韵",
    "S6": "再次抬升并导入副歌",
    "S7": "回返 Hook 并重复主题宣言",
    "S8": "扩写副歌并继续回返",
    "S9": "进入扩展副歌并强化确认",
    "S10": "继续扩展副歌并推高稳定度",
    "S11": "终段回收，完成收束",
}

SEGMENT_BLUEPRINTS = [
    ("S1", "第一轮·主歌", "主歌", "R1", "L01", "L04"),
    ("S2", "第一轮·预副歌", "预副歌", "R1", "L05", "L07"),
    ("S3", "第一轮·副歌一", "副歌一", "R1", "L08", "L11"),
    ("S4", "第一轮·副歌二", "副歌二", "R1", "L12", "L15"),
    ("S5", "第二轮·主歌", "主歌", "R2", "L16", "L18"),
    ("S6", "第二轮·预副歌", "预副歌", "R2", "L19", "L21"),
    ("S7", "第二轮·副歌一", "副歌一", "R2", "L22", "L25"),
    ("S8", "第二轮·副歌二", "副歌二", "R2", "L26", "L29"),
    ("S9", "扩展副歌一", "扩展副歌", "R3", "L30", "L33"),
    ("S10", "扩展副歌二", "扩展副歌", "R3", "L34", "L37"),
    ("S11", "结尾", "结尾", "R3", "L38", "L39"),
]


def segment_lyrics(lines: list[LyricLine]) -> list[SegmentBoundary]:
    known_ids = {line.line_id for line in lines}
    segments: list[SegmentBoundary] = []

    for segment_id, name, role, round_id, line_start, line_end in SEGMENT_BLUEPRINTS:
        if line_start not in known_ids or line_end not in known_ids:
            raise ValueError(f"Missing line range for {segment_id}: {line_start}-{line_end}")
        segments.append(
            SegmentBoundary(
                segment_id=segment_id,
                name=name,
                role=role,
                round_id=round_id,
                line_start=line_start,
                line_end=line_end,
                structural_task=STRUCTURAL_TASKS[segment_id],
            )
        )

    return segments


def detect_segments(lines: list[LyricLine]) -> list[SegmentBoundary]:
    return segment_lyrics(lines)
