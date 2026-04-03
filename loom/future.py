# Represents the result of an async task, allowing callers to block until the result is ready
import threading

class LoomFuture:
    def __init__(self):
        self._state = "PENDING"
        self._result = None
        self._exception = None
        self._event = threading.Event()

    def set_result(self, result):
        if self._state != "PENDING":
            raise RuntimeError("Future is already resolved")
        self._result = result
        self._state = "DONE"
        self._event.set()

    def set_exception(self, exc):
        if self._state != "PENDING":
            raise RuntimeError("Future is already resolved")
        self._exception = exc
        self._state = "FAILED"
        self._event.set()

    def result(self, timeout=30):
        self._event.wait(timeout)
        if self._state == "FAILED":
            raise self._exception
        return self._result

    def done(self):
        return self._state != "PENDING"
    