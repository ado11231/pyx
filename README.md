# pyx++

A collection of low-level Python performance libraries that push CPython beyond its defaults.

## Packages

### [loom](./loom/)
True CPU parallelism for Python using sub-interpreters — async-style API, zero-copy shared memory, no pickle overhead. Requires Python 3.12+.

### [jitctl](./jitctl/)
Hints-based developer control over CPython's JIT compiler via decorators (`@jit_focus`, `@jit_ignore`, `@jit_once`). Targets Python 3.13+. Currently in design/planning phase — see [jitctl/PLANNING.md](./jitctl/PLANNING.md).

## Install

Each package is installed independently:

```bash
# loom
pip install -e ".[dev]"

# jitctl (once implemented)
cd jitctl && pip install -e ".[dev]"
```
