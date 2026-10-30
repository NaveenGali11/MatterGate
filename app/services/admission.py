"""Bounded admission controls for the single-worker public demonstration."""
import time
from collections import deque
from threading import RLock


class AdmissionError(Exception):
    pass


class RequestLimits:
    def __init__(self):
        self.entries = {}
        self.lock = RLock()

    def check(self, workspace, address=None):
        with self.lock:
            stamp = time.monotonic()
            for key in list(self.entries):
                queue = self.entries[key]
                while queue and stamp - queue[0] >= 60:
                    queue.popleft()
                if not queue:
                    del self.entries[key]
            keys = [("workspace:" + workspace, 6)]
            if address is not None:
                keys.append(("address:" + address, 20))
            if len(self.entries) + len(keys) > 4096:
                raise AdmissionError("SERVER_BUSY")
            if any(len(self.entries.get(key, ())) >= limit for key, limit in keys):
                raise AdmissionError("RUN_LIMIT_REACHED")
            for key, _ in keys:
                self.entries.setdefault(key, deque()).append(stamp)
