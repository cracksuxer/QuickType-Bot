import os
from typing import Dict

from rich.traceback import install
from rich.console import Console
import pyautogui
import pygetwindow as gw

console = Console()

install()


class WindowSize:
    """A class for window sizes."""

    def __init__(
        self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int
    ):
        self.top_left = (top_left_x, top_left_y)
        self.bottom_right = (bottom_right_x, bottom_right_y)


def fetch_active_browsers() -> Dict[str, gw.Window]:
    active_browsers: list[gw.Window] = []
    browser_names = ["Firefox", "Chrome", "Edge", "Brave"]
    for browser in browser_names:
        console.log(f"Fetching {browser} windows...")
        browser_windows = gw.getWindowsWithTitle(browser)
        active_browsers.extend(browser_windows)

    browser_titles = {}
    for browser in active_browsers:
        browser_titles[browser.title] = browser

    return browser_titles


def take_screenshot(window: gw.Window, path: str = "") -> str:
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")

    n_screenshots = len(os.listdir("screenshots")) + 1 if path == "" else len(
        os.listdir(path)
    ) + 1
    sc_path = (
        f"screenshots/screenshot_ocr{n_screenshots}.png"
        if path == ""
        else path + f"/screenshot_cc{n_screenshots}.png"
    )

    # window.show()
    # window.activate()
    # window.maximize()

    # time.sleep(0.5)

    if window:
        rect_width = int(window.width - (window.width * 1 / 8))
        rect_height = int(window.height * 1 / 2.8)

        start_x = int(window.topleft[0] + (window.width - rect_width) / 2)
        start_y = int(window.topleft[1] + (window.height - rect_height) / 2)

        pyautogui.screenshot(
            region=(
                start_x,  # X coordinate
                start_y,  # Y coordinate
                rect_width,  # Width of the rectangle
                rect_height,  # Height of the rectangle
            )
        ).save(sc_path)

        return sc_path

    console.log("Window not found or OS not supported.", style="red")
    raise RuntimeError("Window not found or OS not supported.")
