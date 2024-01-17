from concurrent.futures import thread
import threading as th
import time

import cv2
import pygetwindow as gw
import pyautogui

from rich.console import Console
from rich.traceback import install
from quicktype.data_manager import DataManager
from quicktype.ocrManager import OcrManager
from quicktype.screenshot import take_screenshot
from quicktype.simulate_typing import Typer

ocr_thread_termination = True
typer_thread_termination = True


console = Console()
install()


def start_typer(
    data_manager: DataManager, max_interval_delay: float, typer_finished_event: th.Event
):
    typer = Typer()
    while typer_thread_termination:
        word = data_manager.take()
        if word:
            typer.type_string(word + " ", max_interval_delay)

    typer_finished_event.set()


def run_ocr(
    data_manager: DataManager, window: gw.Window, typer_finished_event: th.Event
) -> None:
    """Runs the OCR loop"""
    ocr_manager = OcrManager()
    ocr_manager.link_data_manager(data_manager)

    try:
        while ocr_thread_termination:
            console.log(f"thread termination: {ocr_thread_termination}")
            sc_path = take_screenshot(window)
            ocr_manager.get_image_text(sc_path, "spa", typer_finished_event)
            with data_manager._condition:
                data_manager._condition.wait()
    except Exception as e:
        console.log("el hilo de typer acabo", style="bold red")
        return


def start_typing(window: gw.Window, max_interval_delay: float) -> None:
    """Starts the typing loop."""
    # Activate window
    window.show()
    window.activate()
    window.maximize()
    time.sleep(0.5)

    # refresh page
    pyautogui.press("f5")
    time.sleep(2)

    pyautogui.moveTo(window.center)
    pyautogui.click()

    pyautogui.write(".")
    pyautogui.press("backspace")

    data_manager = DataManager()

    typer_finished_event = th.Event()

    try:
        ocr_thread = th.Thread(
            target=run_ocr,
            name="ocr_thread",
            args=(data_manager, window, typer_finished_event),
        )
        typer_thread = th.Thread(
            target=start_typer,
            name="typer_thread",
            args=(data_manager, max_interval_delay, typer_finished_event),
        )
    except Exception as e:
        console.log(e)
        typer_finished_event.set()
        return

    ocr_thread.start()
    typer_thread.start()

    times = 0

    while True:
        # for _ in range(10):
        sc_path = take_screenshot(window)
        if times == 0:
            console.log("Waiting for OCR to start", style="yellow")
            time.sleep(10)
        else:
            time.sleep(3)
        sc_path2 = take_screenshot(window)

        if (cv2.imread(sc_path) == cv2.imread(sc_path2)).all():
            console.log("Both screenshots are equal", style="bold purple")
            global ocr_thread_termination
            global typer_thread_termination
            ocr_thread_termination = False
            typer_thread_termination = False
            break

        times += 1

    console.log("Typing finished", style="green")
