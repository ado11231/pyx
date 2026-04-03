# loom

True CPU parallelism for Python using sub interpreters — async-style API, zero-copy shared memory, no pickle overhead.

---

## The problem

Python can't easily use all your CPU cores at once. The GIL forces threads to take turns, and multiprocessing works around it by spawning heavy separate processes that copy all your data through pickle.

Loom takes a different approach. It uses Python 3.12+'s sub interpreters — each with their own GIL — running inside one process, sharing memory directly. No pickle, no copying, no heavy process overhead.

---

## Benchmark

```
Single Core:  1.2731 seconds
Loom (4 workers):  0.1980 seconds

6.4x speedup
```

---

## Requirements

- Python 3.12 or higher
- numpy

---

## Installation

Install directly from GitHub:

```bash
pip install git+https://github.com/ado11231/loom.git
```

Or clone and install locally:

```bash
git clone https://github.com/ado11231/loom.git
cd loom
pip install -e .
```

---

## Quick start

```python
import numpy as np
from loom.pool import InterpreterPool
from loom.dispatcher import Dispatcher

# define a cpu heavy function
# important: all imports must be inside the function
def process(data):
    import numpy as np
    result = np.sqrt(np.abs(data * 1.1 + data / 1.5))
    return result

# generate some data
chunks = [np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8) for _ in range(100)]

# run in parallel with loom
with InterpreterPool(workers=4) as pool:
    dispatcher = Dispatcher(pool)

    futures = [dispatcher.submit(process, (chunk,)) for chunk in chunks]
    results = [f.result() for f in futures]

    dispatcher.shutdown()
```

---

## How it works

```
Your code
    ↓
Dispatcher        creates a Future, submits task to thread pool
    ↓
InterpreterPool   manages N sub interpreters, each with own GIL
    ↓
SharedArray       numpy arrays live in shared memory, zero copy
    ↓
Sub Interpreter   runs your function truly in parallel on its own core
    ↓
Future            result comes back, no pickling needed
```

---

## The one rule

Every function you submit must be **self contained** — all imports must live inside the function itself. Sub interpreters start completely blank with no imports or variables from your main program.

```python
# correct — imports inside the function
def my_task(data):
    import numpy as np
    return np.mean(data, axis=2)

# will fail — np not available in sub interpreter
import numpy as np
def my_task(data):
    return np.mean(data, axis=2)
```

---

## When to use loom

| Use case | Good fit? |
|---|---|
| Heavy numpy computation | Yes |
| Image or signal processing | Yes |
| Data transformation pipelines | Yes |
| Waiting on files or networks | No — use asyncio instead |
| Non-numpy data | Not yet |
| Python below 3.12 | No |

---

## Project structure

```
loom/
├── loom/
│   ├── __init__.py       public API
│   ├── pool.py           interpreter pool manager
│   ├── dispatcher.py     task scheduler
│   ├── future.py         result placeholder
│   ├── memory.py         zero copy shared memory
│   └── exceptions.py     custom error types
├── tests/
├── examples/
│   └── image_processing.py   benchmark demo
└── pyproject.toml
```

---

## Status

Early prototype. Core functionality works and is benchmarked. Not production ready yet.

- Sub interpreter cycling works
- Zero copy numpy sharing works
- 6x speedup demonstrated on CPU bound workloads
- Tests in progress
- Non-numpy data types not yet supported

---

## License

MIT
