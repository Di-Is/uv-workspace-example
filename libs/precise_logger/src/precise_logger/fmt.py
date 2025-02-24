"""フォーマッターを提供."""

from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_MAX_DIGITS = 6


class PreciseTimestampFormatter(logging.Formatter):
    """ISO8601 / RFC3339 形式のタイムスタンプ(例: 2025-02-23T12:34:56.123+09:00)を出力するフォーマッター."""

    def __init__(  # noqa: PLR0913
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: str = "%",
        frac_digits: int = 3,
        tz: str | None = None,
        *,
        validate: bool = True,
    ) -> None:
        """コンストラクタ.

        Args:
        fmt: _description_. Defaults to None.
        datefmt: _description_. Defaults to None.
        style: _description_. Defaults to "%".
        frac_digits: _description_. Defaults to 3.
        tz: _description_. Defaults to None.
        validate: _description_. Defaults to True.
        """
        if frac_digits < 0:
            msg = "frac_digits must be non-negative"
            raise ValueError(msg)
        super().__init__(fmt=fmt, datefmt=datefmt, style=style, validate=validate)
        self.frac_digits = frac_digits
        self.tz = tz
        if tz is not None:
            try:
                self._tzinfo = ZoneInfo(tz)
            except Exception as e:
                msg = f"Invalid timezone: {tz}"
                raise ValueError(msg) from e
        else:
            self._tzinfo = None

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:  # noqa: ARG002, D102, N802
        # tz が指定されている場合はそのタイムゾーンで、なければシステムのローカルタイムゾーンで日時を取得
        if self.tz is not None:
            dt = datetime.fromtimestamp(record.created, tz=self._tzinfo)
        else:
            dt = datetime.fromtimestamp(record.created).astimezone()

        # 日付・時刻部分の生成 (例: "2025-02-23T12:34:56")
        time_str = dt.strftime("%Y-%m-%dT%H:%M:%S")

        # 小数部分の生成
        if self.frac_digits > 0:
            # microsecond は常に6桁の数字である
            micro_str = f"{dt.microsecond:06d}"
            if self.frac_digits <= DEFAULT_MAX_DIGITS:
                fractional = micro_str[: self.frac_digits]
            else:
                # frac_digits が6桁を超える場合は、6桁分のmicrosecondに不足分の0を埋める
                fractional = micro_str + "0" * (self.frac_digits - DEFAULT_MAX_DIGITS)
            time_str = f"{time_str}.{fractional}"

        # タイムゾーン部分の生成
        # %z は +0900 のように出力するため、コロンを挿入して +09:00 の形式に変換
        tz_str = dt.strftime("%z")
        if tz_str:
            tz_str = tz_str[:3] + ":" + tz_str[3:]
        time_str += tz_str

        return time_str
