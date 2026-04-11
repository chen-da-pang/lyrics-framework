from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class LyricLine:
    line_id: str
    text: str
    index: int


@dataclass(slots=True)
class SegmentBoundary:
    segment_id: str
    name: str
    role: str
    round_id: str
    line_start: str
    line_end: str
    structural_task: str


@dataclass(slots=True)
class LineAnnotation:
    line_id: str
    segment_id: str
    char_count: int
    line_type: str
    semantic_role: str
    rhyme: str
    rhyme_jie: str
    rhyme_group: str
    in_main_rhyme: bool
    rhyme_length: str
    with_prev: bool
    with_next: bool
    remote_rhyme: bool
    inner_rhyme: bool
    is_hook: bool


@dataclass(slots=True)
class SegmentFramework:
    segment_id: str
    name: str
    role: str
    round_id: str
    line_range: str
    line_count: int
    structural_task: str
    rhyme_pattern: str
    rhyme_org: str
    rhyme_vowel: str
    rhyme_strictness: str
    rhyme_tone: str
    rhyme_special: str
    rhyme_scale: str
    rhyme_jie: str


@dataclass(slots=True)
class SongFramework:
    framework_id: str
    song_name: str
    total_lines: int
    total_segments: int
    rounds: int
    rhyme_style: str
    tags: list[str]
    segments: list[SegmentFramework] = field(default_factory=list)
    lines: list[LineAnnotation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)
