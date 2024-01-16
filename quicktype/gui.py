import PySimpleGUI as sg

import threading as th
from quicktype.im2text import get_image_text_and_colors
from quicktype.screenshot import fetch_active_browsers
import pygetwindow as gw


def window_change(prev_active_windows: int) -> bool:
    new_active_windows = len(gw.getAllWindows())
    return prev_active_windows != new_active_windows


def start_gui():
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
            sg.OptionMenu(["Spanish", "English"], default_value="Spanish"),
        ],
        [
            sg.Text("Maximum delay time for bot's typing"),
            sg.Slider(
                range=(0.5, 1), resolution=0.01, default_value=0.5, orientation="h"
            ),
        ],
        [
            sg.Text("Minimum delay time for bot's typing"),
            sg.Slider(
                range=(0.01, 0.49), resolution=0.01, default_value=0.2, orientation="h"
            ),
        ],
        [
            sg.Text("Error rate (percentage)"),
            sg.Slider(
                range=(0.01, 0.15), resolution=0.01, default_value=0.07, orientation="h"
            ),
        ],
        [
            sg.Text("Random delay rate (percentage)"),
            sg.Slider(
                range=(0.01, 0.20), resolution=0.01, default_value=0.08, orientation="h"
            ),
        ],
        [sg.Button("Start"), sg.Button("Cancel")],
    ]

    # Create the Window
    window = sg.Window("QuickType bot", layout)

    prev_active_windows = len(gw.getAllWindows())
    # Event Loop to process "events" and get the "values" of the inputs

    while True:
        print("checking for window change")
        if window_change(prev_active_windows):
            print("updating browser list")
            prev_active_windows = len(gw.getAllWindows())
            active_browsers, browser_titles = fetch_active_browsers()
            window["browser_list"].update(values=browser_titles)

        event, values = window.read(timeout=1000)
        if event in (sg.WIN_CLOSED, "Cancel"):  # if user closes window or clicks cancel
            a = th.enumerate()
            if any([t.name == "bot_writting" for t in a]):
                print("bot is running")

            for active_th in a:
                if active_th.name == "bot_writting":
                    active_th.join()
                    print("bot stopped")

            break

        if event == "Start":
            print("Starting bot...")
            if "bot_writting" in [t.name for t in th.enumerate()]:
                print("bot is running")
                continue

            th.Thread(
                target=get_image_text_and_colors,
                name="bot_writting",
                args=["img/test.png"],
            ).start()

    window.close()
