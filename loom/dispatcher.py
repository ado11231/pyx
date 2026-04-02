from loom.future import LoomFuture
import threading
import inspect
import textwrap
import _interpreters

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
            interp_id = self._pool.acquire()

            code_string = f"""import numpy as np
{textwrap.dedent(inspect.getsource(function))}
__result__ = {function.__name__}(*{args})
"""
            _interpreters.exec(interp_id, code_string)
            
            future.set_result(None)
            self._pool.release(interp_id)
            
        except Exception as e:
            future.set_exception(e)
