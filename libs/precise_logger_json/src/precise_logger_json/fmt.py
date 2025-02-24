"""フォーマッターを提供."""

from __future__ import annotations

from precise_logger import PreciseTimestampFormatter
from pythonjsonlogger.json import JsonFormatter


class PreciseTimestampJsonFormatter(PreciseTimestampFormatter, JsonFormatter):
    """ISO8601 / RFC3339 形式のタイムスタンプ(例: 2025-02-23T12:34:56.123+09:00)を出力するJSON形式のフォーマッター."""

    def __init__(  # noqa: D107
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        frac_digits: int = 3,
        tz: str | None = None,
        **kwargs: dict,
    ) -> None:
        PreciseTimestampFormatter.__init__(
            self,
            fmt=fmt,
            datefmt=datefmt,
            style=style,
            frac_digits=frac_digits,
            tz=tz,
        )
        JsonFormatter.__init__(self, fmt=fmt, datefmt=datefmt, style=style, **kwargs)
