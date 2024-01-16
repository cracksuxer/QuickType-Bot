from ctypes.wintypes import HLOCAL
import pyautogui
from pynput.keyboard import Key, Controller
import time
import numpy as np
import random
from rich.console import Console

console = Console()
keyboard = Controller()

NEAR_KEYWORDS_MAPS = {
    "a": ["q", "w", "s", "z", "x"],
    "á": ["q", "w", "s", "z", "x"],
    "b": ["v", "g", "h", "n"],
    "c": ["x", "d", "f", "v"],
    "d": ["s", "e", "r", "f", "c", "x"],
    "e": ["w", "s", "d", "r"],
    "é": ["w", "s", "d", "r"],
    "f": ["d", "r", "t", "g", "v", "c"],
    "g": ["f", "t", "y", "h", "b", "v"],
    "h": ["g", "y", "u", "j", "n", "b"],
    "i": ["u", "j", "k", "o"],
    "í": ["u", "j", "k", "o"],
    "j": ["h", "u", "i", "k", "m", "n"],
    "k": ["j", "i", "o", "l", "m"],
    "l": ["k", "o", "p"],
    "m": ["n", "j", "k"],
    "n": ["b", "h", "j", "m"],
    "o": ["i", "k", "l", "p"],
    "ó": ["i", "k", "l", "p"],
    "p": ["o", "l"],
    "q": ["w", "a", "s"],
    "r": ["e", "d", "f", "t"],
    "s": ["a", "w", "e", "d", "x", "z"],
    "t": ["r", "f", "g", "y"],
    "u": ["y", "h", "j", "i"],
    "ú": ["y", "h", "j", "i"],
    "v": ["c", "f", "g", "b"],
    "w": ["q", "a", "s", "e"],
    "x": ["z", "s", "d", "c"],
    "y": ["t", "g", "h", "u"],
    "z": ["a", "s", "x"],
    " ": [" "],
    ".": [","],
    ",": ["."],
    "'": ["/"],
    "/": ["'"],
    ";": ["["],
    "[": [";"],
    "]": ["["],
    "-": ["="],
    "=": ["-"],
    "`": ["1"],
    "1": ["`", "2"],
    "2": ["1", "3"],
    "3": ["2", "4"],
    "4": ["3", "5"],
    "5": ["4", "6"],
    "6": ["5", "7"],
    "7": ["6", "8"],
    "8": ["7", "9"],
    "9": ["8", "0"],
    "0": ["9"],
    "~": ["1"],
    "!": ["1"],
    "@": ["2"],
    "#": ["3"],
    "$": ["4"],
    "%": ["5"],
    "^": ["6"],
    "&": ["7"],
    "*": ["8"],
    "(": ["9"],
    ")": ["0"],
}

def type_character(char: str | Key, delay: float = 0.1) -> None:
    """Types a single character with a given delay."""
    keyboard.press(char)
    console.log(f"Typing {char}")
    time.sleep(random.random() * delay)
    keyboard.release(char)
    time.sleep(random.random() * delay)

def type_string(text: str, max_interval_delay: float) -> None:
    """Types a string at a given position with a given delay between keystrokes."""
    pyautogui.click()
    for char in text:
        min_avg_speed = 0.005
        max_avg_speed = 0.03
        medium_avg_speed = min_avg_speed + (max_avg_speed - min_avg_speed) / 2
        avg_speed = np.random.choice([min_avg_speed, medium_avg_speed, max_avg_speed])
        random_delay = np.random.normal(avg_speed, 0.02, 1000)  #
        clipped_delay = np.random.choice(np.clip(random_delay, 0, max_interval_delay))

        type_character(char)
        time.sleep(clipped_delay)

        if random.random() < 0.07:  #
            random_character_error = random.choice(NEAR_KEYWORDS_MAPS[char.lower()])
            pyautogui.typewrite(random_character_error)

            if random.random() < 0.2:  #
                random_double_character_error = random.choice(NEAR_KEYWORDS_MAPS[random_character_error])
                pyautogui.typewrite(random_double_character_error)
                time.sleep(random.random() * 0.1)
                type_character(Key.backspace)

            time.sleep(random.random() * 0.1)
            type_character(Key.backspace)
            

        if random.random() < 0.08:  #
            time.sleep(random.uniform(0.1, 0.3))
