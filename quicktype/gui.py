import PySimpleGUI as sg

from typing import Dict

import threading as th

from quicktype.im2text import get_image_text_and_colors
from quicktype.screenshot import fetch_active_browsers
from quicktype.typing_loop import start_typing
import pygetwindow as gw
from quicktype.ocrManager import OcrManager

from rich.console import Console
from rich.traceback import install

console = Console()
install()

def window_change(prev_active_windows: int) -> bool:
    new_active_windows = len(gw.getAllWindows())
    return prev_active_windows != new_active_windows


LANGUAGE_MAP = {"Spanish": "spa", "English": "eng"}


def start_gui():
    
    active_browsers = Dict[str, gw.Window]
    
    manager = OcrManager()
    sg.theme("DarkAmber")  # Add a touch of color
    # All the stuff inside your window.
    layout = [
        [
            sg.Text(
                "QuickType bot",
                size=(30, 1),
                font=("Helvetica", 25),
                justification="center",
            )
        ],
        [sg.Text("Browser to use:")],
        [
            sg.OptionMenu(
                ["Option 1", "Option 2", "Option 3"],
                default_value="",
                key="browser_list",
            )
        ],
        [],
        [sg.Text("Bot parameters:")],
        [
            sg.Text("Language:"),
            sg.OptionMenu(
                ["Spanish", "English"], default_value="Spanish", key="language"
            ),
        ],
        [
            sg.Text("Maximum delay time for bot's typing"),
            sg.Slider(
                range=(0.5, 1), resolution=0.01, default_value=0.5, orientation="h", key="max_delay"
            ),
        ],
        [
            sg.Text("Minimum delay time for bot's typing"),
            sg.Slider(
                range=(0.01, 0.49), resolution=0.01, default_value=0.2, orientation="h", key="min_delay"
            ),
        ],
        [
            sg.Text("Error rate (percentage)"),
            sg.Slider(
                range=(0.01, 0.15), resolution=0.01, default_value=0.07, orientation="h", key="error_rate"
            ),
        ],
        [
            sg.Text("Random delay rate (percentage)"),
            sg.Slider(
                range=(0.01, 0.20), resolution=0.01, default_value=0.08, orientation="h", key="random_delay_rate"
            ),
        ],
        [sg.Button("Start"), sg.Button("Cancel")],
    ]

    # Create the Window
    window = sg.Window("QuickType bot", layout)

    prev_active_windows = len(gw.getAllWindows())
    # Event Loop to process "events" and get the "values" of the inputs

    while True:
        console.log("checking for window change")
        if window_change(prev_active_windows):
            console.log("updating browser list")
            prev_active_windows = len(gw.getAllWindows())
            active_browsers = fetch_active_browsers()
            window["browser_list"].update(values=active_browsers.keys())

        event, values = window.read(timeout=1000) # type: ignore
        if event in (sg.WIN_CLOSED, "Cancel"):  # if user closes window or clicks cancel
            a = th.enumerate()
            if any([t.name == "bot_writting" for t in a]):
                console.log("bot is running")

            for active_th in a:
                if active_th.name == "bot_writting":
                    active_th.join()
                    console.log("bot stopped")

            break

        if event == "Start":
            console.log("Starting bot...")
            start_typing(active_browsers[values['browser_list']], values["max_delay"]) # type: ignore
            if "bot_writting" in [t.name for t in th.enumerate()]:
                console.log("bot is running")
                continue

            th.Thread(
                target=get_image_text_and_colors,
                name="bot_writting",
                args=["img/test.png"],
            ).start()

            # th.Thread(
            #     target=manager.get_image_text,
            #     name="bot_writting",
            #     args=["img/test.png", LANGUAGE_MAP[values["language"]]]
            # ).start()

    window.close()
