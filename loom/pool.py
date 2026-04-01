import _interpreters

class InterpreterPool:
    def __init__(self, workers):
        self.workers = workers
        self._interpreters = []
        self._shutdown = False

        for _ in range(self.workers):
            interp_id = _interpreters.create()
            self._interpreters.append(interp_id)

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
        return None

    def shutdown(self):
        if self._shutdown:
            return
        self._shutdown = True

        for id in self._interpreters:
            _interpreters.destroy(id)

        self._interpreters.clear()
        print(f"Pool Shutting Down, {self.workers} Instances Destroyed")
