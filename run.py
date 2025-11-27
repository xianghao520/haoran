"""Entry point for running the report automation."""
from __future__ import annotations

from config import Config
from automation import ReportRunner, Selectors
from date_utils import split_range


def parse_user_input(raw: str) -> tuple[str, str]:
    try:
        start_raw, end_raw = raw.strip().split("-")
        if len(start_raw) != 8 or len(end_raw) != 8:
            raise ValueError
        return start_raw, end_raw
    except ValueError as exc:  # pragma: no cover - interactive aid
        raise ValueError("请输入形如 20230101-20231231 的日期范围") from exc


def main() -> None:
    config = Config()
    selectors = Selectors(
        start_input=config.start_input_selector,
        end_input=config.end_input_selector,
        execute_button=config.execute_button_selector,
    )

    user_input = input("请输入日期范围 (例 20230101-20250901)：")
    start_raw, end_raw = parse_user_input(user_input)

    ranges = split_range(start_raw, end_raw, chunk_days=7)
    print(f"共 {len(ranges)} 个区间：{ranges}")

    runner = ReportRunner(config, selectors)
    runner.open()
    input("请在浏览器中完成登录后按回车继续...")

    try:
        runner.run_batch(ranges)
        print("所有日期提交完成。")
    finally:
        runner.close()


if __name__ == "__main__":
    main()
