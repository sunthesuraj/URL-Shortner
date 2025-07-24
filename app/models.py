import datetime
import threading

class URLStore:
    """A thread-safe in-memory storage for URL mappings."""
    def __init__(self):
        self._data = {}
        self._lock = threading.Lock()

    def save_url(self, short_code, long_url):
        with self._lock:
            if short_code in self._data:
                return False
            self._data[short_code] = {
                "long_url": long_url,
                "created_at": datetime.datetime.now(datetime.UTC),
                "clicks": 0
            }
            return True

    def get_url_and_increment_clicks(self, short_code):
        with self._lock:
            if short_code in self._data:
                self._data[short_code]['clicks'] += 1
                return self._data[short_code]['long_url']
        return None

    def get_stats(self, short_code):
        with self._lock:
            return self._data.get(short_code, None)

    def is_code_available(self, short_code):
        with self._lock:
            return short_code not in self._data

url_store = URLStore()