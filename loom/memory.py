import numpy as np
from multiprocessing.shared_memory import SharedMemory

class SharedArray:
    def __init__(self, array):
        self._shm = SharedMemory(create = True, size = array.nbytes)
        self._shared_array = np.ndarray(array.shape, dtype = array.dtype, buffer = self._shm.buf)
        self._shared_array[:] = array[:]
        self._shape = array.shape
        self._dtype = array.dtype

    def get(self):
        return self._shared_array
    
    def close(self):
        self._shm.close()
        self._shm.unlink()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return None