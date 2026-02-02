# utils/cache.py
import time

class TTLCache:
    def __init__(self, ttl: int):
        self.ttl = ttl
        self._data = {}

    def get(self, key):
        item = self._data.get(key)
        if not item:
            return None

        value, timestamp = item
        if time.time() - timestamp > self.ttl:
            del self._data[key]
            return None

        return value

    def set(self, key, value):
        self._data[key] = (value, time.time())
