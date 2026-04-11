from .annotator import annotate_lines
from .generator import build_framework, generate_framework, write_framework_outputs
from .loader import load_lyric_lines, load_rhyme_audit
from .models import LineAnnotation, LyricLine, SegmentBoundary, SegmentFramework, SongFramework
from .segmenter import detect_segments
from .taxonomy import ALLOWED_SEMANTIC_ROLES

__all__ = [
    "ALLOWED_SEMANTIC_ROLES",
    "LineAnnotation",
    "LyricLine",
    "SegmentBoundary",
    "SegmentFramework",
    "SongFramework",
    "annotate_lines",
    "build_framework",
    "detect_segments",
    "generate_framework",
    "load_lyric_lines",
    "load_rhyme_audit",
    "write_framework_outputs",
]
