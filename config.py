from pathlib import Path
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Holds constants required by the automation runner."""

    # 页面地址，后续如需切换报告可在此修改
    base_url: str = "https://base.cmcm.com:8080/bi/report?product_id=1"

    # ChromeDriver 路径。留空则使用 Selenium Manager 自动下载。
    chromedriver_path: Optional[Path] = Path.home() / "drivers" / "chromedriver"


    # Selenium 等待设置
    implicit_wait_seconds: int = 5
    explicit_wait_seconds: int = 20

    # 页面元素选择器
    start_input_selector: str = "#startdateall"
    end_input_selector: str = "#dateall"
    execute_button_selector: str = "div.run-sql button.btn.btn-primary.btn-xs"
