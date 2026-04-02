class LoomFuture:
    def __init__(self):
        self._state = "PENDING"
        self._result = None
        self._exception = None

    def set_result(self, result):
        if self._state != "PENDING":
            raise RuntimeError("Future is already resolved")
        self._result = result
        self._state = "DONE"

    def set_exception(self, exc):
        if self._state != "PENDING":
            raise RuntimeError("Future is already resolved")
        self._exception = exc
        self._state = "FAILED"

    def result(self):
        if self._state == "PENDING":
            raise RuntimeError("Not Ready Yet")
        elif self._state == "FAILED":
            raise self._exception
        elif self._state == "DONE":
            return self._result
        
    def done(self):
        return self._state != "PENDING"
        

