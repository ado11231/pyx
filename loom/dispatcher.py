from loom.future import LoomFuture
import threading

class Dispatcher: 
    def __init__(self, pool):
        self._pool = pool

    def submit(self, function, args):
        future = LoomFuture()
        thread = threading.Thread(target = self._run_task, args = (future, function, args))
        thread.start()
        return future

    def _run_task(self, future, function, args):
        try:
            result = function(*args)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)
