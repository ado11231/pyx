from loom.future import LoomFuture
from loom.memory import SharedArray
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import threading
import inspect
import textwrap
import _interpreters

class Dispatcher: 
    def __init__(self, pool):
        self._pool = pool
        self._executor = ThreadPoolExecutor(max_workers = pool.workers)

    def submit(self, function, args):
        future = LoomFuture()
        self._executor.submit(self._run_task, future, function, args)
        return future

    def _run_task(self, future, function, args):
        try:
            input_shared = SharedArray(args[0])
            output_array = np.zeros(args[0].shape[:2], dtype=np.float64)
            output_shared = SharedArray(output_array)

            interp_id = self._pool.acquire()
            code_string = """
x = 1 + 1
"""
            _interpreters.exec(interp_id, code_string)
            
            result = output_shared.get().copy()
            future.set_result(result)

            input_shared.close()
            output_shared.close()
            
        except Exception as e:
            print(f"Task Failed: {e}")
            future.set_exception(e)
