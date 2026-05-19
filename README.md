# pyx++

A collection of low-level Python performance libraries that push CPython beyond its defaults.

---

## Packages

### [sharedx](./sharedx/)

True CPU parallelism for Python using CPython sub-interpreters — async-style API, zero-copy shared memory, no pickle overhead. Requires Python 3.12+.

```
Single Core:      1.2731s
Sharedx (4 workers):  0.1980s   →  6.4x speedup
```

### [jitctl](./jitctl/)

Hints-based developer control over CPython's JIT compiler via decorators (`@jit_focus`, `@jit_ignore`, `@jit_once`). Targets Python 3.13+. Currently in design/planning phase — see [jitctl/PLANNING.md](./jitctl/PLANNING.md).

---

## Install

Each package is installed independently.

```bash
# sharedx
pip install git+https://github.com/ado11231/pyx-plus-plus.git#subdirectory=sharedx

# or clone and install locally
git clone https://github.com/ado11231/pyx-plus-plus.git
cd pyx-plus-plus/sharedx
pip install -e .
```

---

## Quick start (sharedx)

```python
import numpy as np
from sharedx.pool import InterpreterPool
from sharedx.dispatcher import Dispatcher

# All imports must be inside the function — sub-interpreters start blank
def process(data):
    import numpy as np
    return np.sqrt(np.abs(data * 1.1 + data / 1.5))

chunks = [np.random.randint(0, 255, (256, 256, 3), dtype=np.uint8) for _ in range(100)]

with InterpreterPool(workers=4) as pool:
    dispatcher = Dispatcher(pool)
    futures = [dispatcher.submit(process, (chunk,)) for chunk in chunks]
    results = [f.result() for f in futures]
    dispatcher.shutdown()
```

> **The one rule:** every function you submit must be self-contained — all imports must live inside the function body. Sub-interpreters start with no imports or variables from your main program.

---

## How it works

```
Your code
    ↓
Dispatcher        creates a Future, submits task to thread pool
    ↓
InterpreterPool   manages N sub-interpreters, each with its own GIL
    ↓
SharedArray       numpy arrays live in shared memory — zero copy
    ↓
Sub-interpreter   runs your function truly in parallel on its own core
    ↓
Future            result comes back, no pickling needed
```

---

## When to use sharedx

| Use case                     | Good fit?             |
|------------------------------|-----------------------|
| Heavy numpy computation      | Yes                   |
| Image or signal processing   | Yes                   |
| Data transformation pipelines| Yes                   |
| Waiting on files or networks | No — use asyncio      |
| Non-numpy data               | Not yet               |
| Python below 3.12            | No                    |

---

## Status

Early prototype. Core functionality works and is benchmarked. Not production ready.

- Sub-interpreter cycling works
- Zero-copy numpy sharing works
- 6x speedup demonstrated on CPU-bound workloads
- Tests in progress
- Non-numpy data types not yet supported
- jitctl: design/planning phase only

---

## License

MIT
