import logging
import re

from precise_logger import PreciseTimestampFormatter


def create_log_record(created_time: float) -> logging.LogRecord:
    """固定のタイムスタンプを持つ LogRecord を生成するヘルパー関数."""
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname=__file__,
        lineno=0,
        msg="Test message",
        args=None,
        exc_info=None,
    )
    record.created = created_time
    return record


def test_formatter_with_fraction_digits_3():
    """frac_digits=3 の場合の出力を検証.

    固定タイムゾーン tz=+09:00 を指定しているため、UTC の 2023-01-01 00:00:00.123456 は
    2023-01-01T09:00:00.123+09:00 となることを確認
    """
    created_time = 1672531200.123456  # UTC: 2023-01-01 00:00:00.123456
    tz = "Asia/Tokyo"
    formatter = PreciseTimestampFormatter(frac_digits=3, tz=tz)
    record = create_log_record(created_time)
    formatted_time = formatter.formatTime(record)
    expected = "2023-01-01T09:00:00.123+09:00"
    assert formatted_time == expected


def test_formatter_with_fraction_digits_6():
    """frac_digits=6 の場合の出力を検証."""
    created_time = 1672531200.123456
    tz = "Asia/Tokyo"
    formatter = PreciseTimestampFormatter(frac_digits=6, tz=tz)
    record = create_log_record(created_time)
    formatted_time = formatter.formatTime(record)
    expected = "2023-01-01T09:00:00.123456+09:00"
    assert formatted_time == expected


def test_formatter_with_fraction_digits_9():
    """frac_digits=9 の場合の出力を検証."""
    created_time = 1672531200.123456
    tz = "Asia/Tokyo"
    formatter = PreciseTimestampFormatter(frac_digits=9, tz=tz)
    record = create_log_record(created_time)
    formatted_time = formatter.formatTime(record)
    expected = "2023-01-01T09:00:00.123456000+09:00"
    assert formatted_time == expected


def test_formatter_with_no_fraction():
    """frac_digits=0 の場合、タイムスタンプの小数部分が出力されないことを検証."""
    created_time = 1672531200.123456
    tz = "Asia/Tokyo"
    formatter = PreciseTimestampFormatter(frac_digits=0, tz=tz)
    record = create_log_record(created_time)
    formatted_time = formatter.formatTime(record)
    expected = "2023-01-01T09:00:00+09:00"
    assert formatted_time == expected


def test_formatter_with_local_timezone():
    """Tz が None の場合、システムのローカルタイムゾーンが使用され、出力が ISO8601/RFC3339 形式になっていることを正規表現で検証する.

    (ローカルタイムゾーンは環境依存のため、具体的な値はチェックせず形式のみを確認)
    """
    created_time = 1672531200.123456
    formatter = PreciseTimestampFormatter(frac_digits=3, tz=None)
    record = create_log_record(created_time)
    formatted_time = formatter.formatTime(record)
    # パターン例: "YYYY-MM-DDThh:mm:ss.ddd+hh:mm" またはマイナスの場合もあり
    pattern = r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?[\+\-]\d{2}:\d{2}$"
    assert re.match(pattern, formatted_time)
