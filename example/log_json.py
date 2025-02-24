import logging

from precise_logger_json import PreciseTimestampJsonFormatter

# 使用例
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    handler = logging.StreamHandler()
    # フォーマッターをインスタンス化(例: 小数点以下4桁、tz指定なしの場合はローカルタイムゾーンを使用)
    formatter = PreciseTimestampJsonFormatter(
        fmt="%(asctime)s - %(levelname)s - %(message)s",
        frac_digits=9,
        rename_fields={"asctime": "ts", "levelname": "level", "message": "msg"},
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.info("Test")
