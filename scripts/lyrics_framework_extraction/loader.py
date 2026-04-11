from __future__ import annotations

import json
from pathlib import Path

from .models import LyricLine


def load_lyric_lines(path: Path) -> list[LyricLine]:
    rows = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    return [
        LyricLine(line_id=f"L{index:02d}", text=text, index=index)
        for index, text in enumerate(rows, start=1)
    ]


def load_rhyme_audit(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
