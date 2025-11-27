"""Selenium automation logic for the reporting UI."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from config import Config


@dataclass(frozen=True)
class Selectors:
    start_input: str
    end_input: str
    execute_button: str


class ReportRunner:
    """Encapsulates all browser interactions for the report automation."""

    def __init__(self, config: Config, selectors: Selectors):
        options = webdriver.ChromeOptions()
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--allow-insecure-localhost")
        options.add_argument("--user-data-dir=/Users/haoran/ChromeProfileCopy")
        options.add_argument("--profile-directory=Default")
        options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        if config.chromedriver_path is not None:
            service = Service(str(config.chromedriver_path))
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            # 直接调用 Chrome，会由 Selenium Manager 自动下载安装驱动
            self.driver = webdriver.Chrome(options=options)

        self.driver.implicitly_wait(config.implicit_wait_seconds)
        self.wait = WebDriverWait(self.driver, config.explicit_wait_seconds)

        self.config = config
        self.selectors = selectors
        self._focus_target_tab()

    def open(self) -> None:
        """Browser already points to the desired page; nothing to do."""
        return

    def close(self) -> None:
        """Clean up browser resources."""
        self.driver.quit()

    def _focus_target_tab(self) -> None:
        target_host = urlparse(self.config.base_url).hostname
        if not target_host:
            return

        for handle in self.driver.window_handles:
            self.driver.switch_to.window(handle)
            try:
                current_host = urlparse(self.driver.current_url).hostname
            except Exception:
                continue

            if current_host and current_host.endswith(target_host):
                return

        print(
            f"未找到包含 {target_host} 的已打开标签，请确保在启动脚本前已打开目标页面。"
        )

    def _fill_date(self, selector: str, value: str) -> None:
        element = self._locate_clickable(selector)
        self.driver.execute_script(
            "arguments[0].removeAttribute('readonly'); arguments[0].value='';",
            element,
        )
        element.send_keys(value)
        self.driver.execute_script(
            "arguments[0].dispatchEvent(new Event('input', { bubbles: true }));",
            element,
        )

    def _locate_clickable(self, selector: str):
        self.driver.switch_to.default_content()
        try:
            return self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        except TimeoutException:
            pass

        frames = self.driver.find_elements(By.CSS_SELECTOR, "iframe")
        for frame in frames:
            self.driver.switch_to.default_content()
            self.driver.switch_to.frame(frame)
            try:
                return WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            except TimeoutException:
                continue

        self.driver.switch_to.default_content()
        raise TimeoutException(f"未能在页面或 iframe 中找到 {selector} 元素")

    def _click_execute(self) -> None:
        button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, self.selectors.execute_button)))
        button.click()

    def _accept_alert_if_present(self) -> None:
        try:
            alert = self.wait.until(EC.alert_is_present())
            alert.accept()
        except TimeoutException:
            pass

    def run_once(self, start_date: str, end_date: str) -> None:
        self._fill_date(self.selectors.start_input, start_date)
        self._fill_date(self.selectors.end_input, end_date)
        self._click_execute()
        self._accept_alert_if_present()

    def run_batch(self, ranges: Iterable[Tuple[str, str]]) -> None:
        for index, (start_date, end_date) in enumerate(ranges, start=1):
            print(f"[{index}] 提交 {start_date} ~ {end_date}")
            self.run_once(start_date, end_date)
