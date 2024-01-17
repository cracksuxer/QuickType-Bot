import time
import cv2
import pygetwindow as gw
from quicktype.ocrManager import OcrManager
from quicktype.screenshot import take_screenshot
from quicktype.simulate_typing import type_string
import pyautogui

from rich.console import Console
from rich.traceback import install

console = Console()
install()

manager = OcrManager()

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
    
    # Take number of words to type from the input box
    # n_words = int(manager.get_image_text(take_screenshot(window), "spa"))
    # console.log(n_words)
    
    # 3.Loop screenshoting and retrieving text
    # - Take screenshot
    # - Call imag_to_text
    # - Type text
    # Loop continues until it types exactly the number of words
    last_cs_path = ""
    while(True):
        try:
            sc_path = take_screenshot(window)
            
            if last_cs_path != "":
                if (cv2.imread(sc_path) == cv2.imread(last_cs_path)).all():
                    break
            
            last_cs_path = sc_path
            pyautogui.moveTo(window.center) # Por si acaso clicamos al centro en cada palabra
            pyautogui.click()
            sc_text = manager.get_image_text(sc_path, "spa")
            type_string(sc_text + " ", max_interval_delay)
            
        except Exception as e:
            console.log(f"An error occured: {e}", style="red")
            raise e
        
    console.log("Typing finished", style="green")