from future import LoomFuture
import threading


class Dispatcher: 
    def __init__(self, pool):
        self._pool = pool

    def submit(self, function, args):
        future_loom = LoomFuture()
        thread1 = threading.Thread(target = self._run_task, args = (future_loom, function, args))
        thread1.start()
        return future_loom

    def _run_task(self, future, function, args):
        try:
            result = function(*args)
            future.set_result(result)
        except Exception as e:
            future.set_exception(e)




