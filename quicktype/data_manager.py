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
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the manager."""
        self._data = []
        self._lock = th.Lock()
        self._consumed_counter = 0
        self._threshold = 5
        self._condition = th.Condition(self._lock)

    def send(self, single_word: str = "", words_list: List[str] = []):
        """Send data to the manager."""
        with self._lock:
            console.log(f"Sending {single_word} {words_list}")
            if single_word:
                self._data.append(single_word)
            else:
                self._data.extend(words_list)

    def take(self) -> str | None:
        """Take data from the manager."""
        with self._lock:
            if not self._data:
                return None
            word = self._data.pop(0)
            self._consumed_counter += 1
            if self._consumed_counter >= self._threshold:
                self._consumed_counter = 0
                console.log("Notifying...")
                self._condition.notify()
            console.log(f"Taking {word}")
            return word