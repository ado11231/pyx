from loom.future import LoomFuture
from loom.memory import SharedArray
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import inspect
import textwrap
import _interpreters

class Dispatcher: 
    def __init__(self, pool):
        self._pool = pool
        self._executor = ThreadPoolExecutor(max_workers = pool.workers)

    def submit(self, function, args):
        future = LoomFuture()
        input_shared = SharedArray(args[0])
        output_array = np.zeros(args[0].shape[:2], dtype = np.float64)
        output_shared = SharedArray(output_array)
        self._executor.submit(self._run_task, future, function, args, input_shared, output_shared)
        return future
    
    def _run_task(self, future, function, args, input_shared, output_shared):
        interp_id = None
        try:
            interp_id = self._pool.acquire()

            code_string = f"""import numpy as np
from multiprocessing.shared_memory import SharedMemory

{textwrap.dedent(inspect.getsource(function))}

_in_shm = SharedMemory(name="{input_shared._shm.name}", create=False)
_in_arr = np.ndarray({args[0].shape}, dtype=np.{args[0].dtype}, buffer=_in_shm.buf)

_out = {function.__name__}(_in_arr)

_out_shm = SharedMemory(name="{output_shared._shm.name}", create=False)
_out_arr = np.ndarray({args[0].shape[:2]}, dtype=np.float64, buffer=_out_shm.buf)
_out_arr[:] = _out

_in_shm.close()
_out_shm.close()
"""
            _interpreters.exec(interp_id, code_string)
            result = output_shared.get().copy()
            future.set_result(result)

        except Exception as e:
            future.set_exception(e)
        finally:
            if interp_id is not None:
                self._pool.release(interp_id)

            input_shared.close()
            output_shared.close()

    def shutdown(self):
        self._executor.shutdown(wait = True)
