import _interpreters
import queue

class InterpreterPool:
    def __init__(self, workers):
        self.workers = workers
        self._interpreters = []
        self._shutdown = False
        self._free = queue.Queue()

        for _ in range(self.workers):
            interp_id = _interpreters.create()
            self._interpreters.append(interp_id)
            self._free.put(interp_id)

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

    def acquire(self):
        return self._free.get()
        
    def release(self, interp_id):
        self._free.put(interp_id)
