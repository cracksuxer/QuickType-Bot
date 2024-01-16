from ctypes import pythonapi
from platform import python_branch
import time
from matplotlib.mlab import complex_spectrum
import pygetwindow as gw
from quicktype.screenshot import take_screenshot
from quicktype.im2text import get_image_text_and_colors
from quicktype.simulate_typing import type_string
import pyautogui

from rich.console import Console
from rich.traceback import install

console = Console()
install()

def start_typing(window: gw.Window, max_interval_delay: float) -> None:
    # 1.Take number of words to type from the input box
    n_words = 67 # TODO: Placeholder
    
    # 3.Loop screenshoting and retrieving text
    # - Take screenshot
    # - Call imag_to_text
    # - Type text
    # Loop continues until it types exactly the number of words
        
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
    
    for i in range(n_words):
        try:
            sc_path = take_screenshot(window)
            pyautogui.moveTo(window.center) # Por si acaso clicamos al centro en cada palabra
            pyautogui.click()
            sc_text_and_color = get_image_text_and_colors(sc_path)
            if i != 0:
                pyautogui.write(" ")
            type_string(sc_text_and_color[0][0], max_interval_delay)
            
        except Exception as e:
            console.log(f"An error occured: {e}", style="red")
            raise e
        
    console.log("Typing finished", style="green")