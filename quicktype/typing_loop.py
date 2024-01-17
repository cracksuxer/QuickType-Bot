import threading as th
import time
from typing import Literal, Tuple

import cv2
import pygetwindow as gw
import pyautogui

from rich.console import Console
from rich.traceback import install
from quicktype.data_manager import DataManager
from quicktype.ocr_manager import OcrManager
from quicktype.screenshot import take_screenshot
from quicktype.simulate_typing import Typer

import cv2 as cv

ocr_thread_termination = True
typer_thread_termination = True
check_new_line_thread_termination = True

console = Console()
install()


def check_new_line(
    window: gw.Window, ocr_manager: OcrManager, data_manager: DataManager
):
    aux_whie_count = 0

    """Checks if the line has changed."""
    while check_new_line_thread_termination:
        white_count = 0
        sc_path = take_screenshot(window, "new_line_condition")
        image = cv.imread(sc_path)
        gray_image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)

        threshold_value = 90
        _, binary_image = cv.threshold(
            gray_image, threshold_value, 255, cv.THRESH_BINARY
        )

        text_regions = ocr_manager._segment_text_regions_with_dilation(binary_image)
        sorted_regions = ocr_manager._sort_text_regions(text_regions)

        for _, regions in sorted_regions.items():
            for region in regions:
                region_color = ocr_manager._determine_region_color(region, gray_image)

                if region_color == "white":
                    white_count += 1
                    continue

        if aux_whie_count > white_count:
            console.log("New line detected", style="bold green")
            data_manager.notify_ocr()

        aux_whie_count = white_count
        time.sleep(0.5)

    console.log("check_new_line_thread terminated", style="bold red")


def start_typer(
    data_manager: DataManager,
    typer_finished_event: th.Event,
    delay: Tuple[float, float],
    error_rate: float,
    random_delay_rate: float,
):
    typer = Typer()
    while typer_thread_termination:
        word = data_manager.take()
        if word:
            typer.type_string(word + " ", delay, error_rate, random_delay_rate)

    console.log(f"ocr_thread alive: {ocr_thread_termination}")
    typer_finished_event.set()

def run_ocr(
    data_manager: DataManager,
    window: gw.Window,
    typer_finished_event: th.Event,
    lang: Literal["spa", "eng"] = "spa",
) -> None:
    """Runs the OCR loop"""
    ocr_manager = OcrManager()
    ocr_manager.link_data_manager(data_manager)

    only_line_3 = 0

    try:
        while ocr_thread_termination:
            console.log("OCR thread running", style="bold yellow")
            sc_path = take_screenshot(window)

            ocr_manager.get_image_text(sc_path, lang, typer_finished_event, only_line_3)

            with data_manager._condition:
                console.log("Waiting for end line...", style="yellow")
                data_manager._condition.wait()

            only_line_3 = 3

    except Exception as e:
        console.log(e)
        console.log("OCR thread terminated", style="bold red")
        return


def start_typing(
    window: gw.Window,
    lang: Literal["spa", "eng"],
    delay: Tuple[float, float],
    error_rate: float,
    random_delay_rate: float,
) -> None:
    """Starts the typing loop."""
    global ocr_thread_termination
    global typer_thread_termination
    global check_new_line_thread_termination
    ocr_thread_termination = True
    typer_thread_termination = True
    check_new_line_thread_termination = True

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
            args=(data_manager, window, typer_finished_event, lang),
        )
        typer_thread = th.Thread(
            target=start_typer,
            name="typer_thread",
            args=(data_manager, typer_finished_event, delay, error_rate, random_delay_rate),
        )
        new_line_check_thread = th.Thread(
            target=check_new_line,
            name="new_line_check_thread",
            args=(window, OcrManager(), data_manager),
        )
    except Exception as e:
        console.log(e)
        typer_finished_event.set()
        return

    ocr_thread.start()
    typer_thread.start()
    new_line_check_thread.start()

    once_condition = True

    while True:
        sc_path = take_screenshot(window, "stop_condition")
        if once_condition:
            once_condition = False
            console.log("Waiting for OCR to start", style="yellow")
            time.sleep(7)

        time.sleep(4)
        sc_path2 = take_screenshot(window, "./stop_condition")

        if (cv2.imread(sc_path) == cv2.imread(sc_path2)).all():
            console.log(
                f"Screenshot {sc_path} is the same as {sc_path2}", style="yellow"
            )
            ocr_thread_termination = False
            typer_thread_termination = False
            check_new_line_thread_termination = False
            break

    console.log("Typing finished", style="green")

    console.log(data_manager.final_phrase, style="bold green")

    active_windwos = gw.getAllWindows()
    for window in active_windwos:
        if window.title == "QuickType bot":
            window.show()
            window.activate()
            break
