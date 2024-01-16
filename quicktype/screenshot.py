from typing import Optional, Union
from sys import platform

import subprocess
from rich.traceback import install
from rich.console import Console
import pyautogui
import pygetwindow as gw

console = Console()

install()

class WindowSize:
    """A class for window sizes."""
    def __init__(self, top_left_x: int, top_left_y: int, bottom_right_x: int, bottom_right_y: int):
        self.top_left = (top_left_x, top_left_y)
        self.bottom_right = (bottom_right_x, bottom_right_y)

def fetch_active_browsers() -> (list[gw.Window], list[str]):
    active_browsers: list[gw.Window] = []
    browser_names = ["Firefox", "Chrome", "Edge", "Brave"]
    for browser in browser_names:
        console.log(f"Fetching {browser} windows...")
        browser_windows = gw.getWindowsWithTitle(browser)
        active_browsers.extend(browser_windows)

    browser_titles: list[str] = [browser.title for browser in active_browsers]
    return active_browsers, browser_titles

def take_window_pos(window_name: str) -> Optional[WindowSize]:
    """Takes a screenshot of the window with the given name."""
    if platform == "linux":
        try:
            window_id = subprocess.check_output(
                ['xdotool', 'search', '--name', window_name]
            ).decode().strip()
            geometry_output = subprocess.check_output(
                ['xdotool', 'getwindowgeometry', '--shell', window_id]
            ).decode()

            x, y, width, height = 0, 0, 0, 0  # Default values
            for line in geometry_output.split('\n'):
                if line.startswith('X='):
                    x = int(line.split('=')[1])
                elif line.startswith('Y='):
                    y = int(line.split('=')[1])
                elif line.startswith('WIDTH='):
                    width = int(line.split('=')[1])
                elif line.startswith('HEIGHT='):
                    height = int(line.split('=')[1])

            x2, y2 = x + width, y + height

            return WindowSize(x, y, x2, y2)
        except subprocess.CalledProcessError:
            console.log("Window not found.", style="bold red")
            return None

    elif platform == "win32":
        window_list = gw.getWindowsWithTitle(window_name)
        window = None
        if len(window_list) > 0:
            window = window_list[0]
        if window:
            console.log(window.left, window.top, window.right, window.bottom)
            return WindowSize(window.left, window.top, window.right, window.bottom)

        console.log("Window not found.", style="bold red")
        return None
    else:
        console.log("OS not supported.", style="bold red")
        return None

windowSpecs: Union[WindowSize, None] = take_window_pos("Code")

if windowSpecs:
    width = windowSpecs.bottom_right[0] - windowSpecs.top_left[0]
    height = windowSpecs.bottom_right[1] - windowSpecs.top_left[1]

    pyautogui.screenshot(region=(
        windowSpecs.top_left[0],
        windowSpecs.top_left[1],
        width,
        height
    )).save("screenshot.png")
else:
    print("Window not found or OS not supported.")
