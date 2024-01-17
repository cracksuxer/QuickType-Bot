import threading as th
from typing import List

class DataManager:
    """Manager data to send and receive asynchronously."""
    _instace = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._data: List[str] = []
            cls._lock = th.Lock()
        return cls._instance

    def send(self, data: str):
        """Send data to the manager."""
        with self._lock:
            self._data.append(data)

    def take(self) -> str | None:
        """Take data from the manager."""
        if not self._data:
            return None
        
        with self._lock:
            return self._data.pop(0)