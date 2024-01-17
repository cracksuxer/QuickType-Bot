import threading as th
from typing import List

from rich.console import Console
from rich.traceback import install

console = Console()
install()

class DataManager:
    """Manager data to send and receive asynchronously."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DataManager, cls).__new__(cls)
            cls._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the manager."""
        self._initialized = False
        if not self._initialized:
            self._data = []
            self._lock = th.Lock()
            self._condition = th.Condition(self._lock)
            self._initialized = True
            self._final_phrase = ""
            
    @property 
    def final_phrase(self) -> str:
        """Get the final phrase."""
        return self._final_phrase
    
    def notify_ocr(self):
        """Get the condition to notify."""
        with self._lock:
            self._condition.notify()

    def send(self, single_word: str = "", words_list: List[str] = []):
        """Send data to the manager."""
        with self._lock:
            if single_word not in ["i", "c", "[]", None]:
                console.log(f"OCR[{single_word}] -> DM")
                self._data.append(single_word)
            elif words_list:
                self._data.extend(words_list)
            else:
                console.log("No data to send", style="bold red")

    def take(self) -> str | None:
        """Take data from the manager."""
        with self._lock:
            if not self._data:
                return None
            word = self._data.pop(0)
            self._final_phrase += " " + word
            console.log(f"TyPer <- DM[{word}]")
            return word