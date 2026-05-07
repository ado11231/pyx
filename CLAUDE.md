# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repo structure

This is a monorepo called **pyx++** with two independent Python packages:

```
pyx++/              ← repo root
  sharedx/          ← sharedx package source
  jitctl/           ← jitctl package (scaffold only — not yet implemented)
    jitctl/         ← jitctl package source (stubs)
    PLANNING.md     ← design doc and open questions for future implementation
  pyproject.toml    ← sharedx build config
```

Each package has its own `pyproject.toml` and is installed independently. They share no code and have no dependency on each other.

---

## sharedx

True CPU parallelism for Python using CPython sub-interpreters (`_interpreters`, available in Python 3.12+). Async-style API, zero-copy shared memory, no pickle overhead.

**Requires Python 3.12+**

### Commands

```bash
# Install (editable + dev deps)
pip install -e ".[dev]"

# Run all tests
pytest

# Run a single test
pytest tests/test_foo.py::test_name

# Run the benchmark example
python examples/image_processing.py
```

### Architecture

The execution flow: `InterpreterPool` → `Dispatcher` → `SharedxFuture`.

**`InterpreterPool` (`sharedx/pool.py`)** — creates N sub-interpreters at startup via `_interpreters.create()` and manages them in a `queue.Queue` for acquire/release. Supports the context manager protocol; `__exit__` calls `shutdown()` which destroys all interpreters.

**`Dispatcher` (`sharedx/dispatcher.py`)** — the core task runner. Uses a `ThreadPoolExecutor` (one thread per worker) to submit tasks asynchronously. For each task it:
1. Wraps input/output numpy arrays in `SharedArray` (shared memory).
2. Serializes the user function with `inspect.getsource()` + `textwrap.dedent()`.
3. Injects the function source and shared-memory attachment code as a string into an acquired sub-interpreter via `_interpreters.exec()`.
4. Copies the result out of the output `SharedArray` and resolves the `SharedxFuture`.

**`SharedArray` (`sharedx/memory.py`)** — wraps a numpy array in `multiprocessing.SharedMemory` so it's accessible across interpreter boundaries without pickling. Both interpreters attach to the same block by name.

**`SharedxFuture` (`sharedx/future.py`)** — a simple future backed by `threading.Event`. Callers block on `.result(timeout=30)`.

### Key constraints

- Functions passed to `Dispatcher.submit()` must be **top-level and inspect-able** — `inspect.getsource()` is used to serialize them as strings. Lambdas, closures, and methods sourced from a REPL will fail.
- `Dispatcher.submit()` currently expects `args[0]` to be a numpy array (it hard-codes `SharedArray(args[0])` and `.shape`/`.dtype` access). Generalizing beyond numpy arrays requires reworking the dispatcher.
- Sub-interpreters have **isolated module state** — each interpreter re-imports everything from scratch, so any setup (imports, initialization) must be included in the generated code string inside `_run_task`.

---

## jitctl

**Status: scaffold only — do not implement yet. See `jitctl/PLANNING.md` for full design doc and open questions.**

Hints-based developer control over CPython's JIT compiler via decorators (`@jit_focus`, `@jit_ignore`, `@jit_once`). Targets Python 3.13/3.14 where no native per-function JIT API exists. Uses warm-up loops and profiling today, with a version-aware backend layer designed to swap in real CPython JIT hooks when they are eventually exposed.

**Requires Python 3.13+**

### Commands (once implemented)

```bash
cd jitctl
pip install -e ".[dev]"
pytest
```

### Architecture (planned)

- `__init__.py` — the three public decorators, nothing else
- `_backend.py` — **the only module that checks Python version**; routes to the right strategy
- `_warmup.py` — calls a function N times with dummy args to trigger JIT tier promotion
- `_profiler.py` — wraps functions to track call count and timing
- `_introspect.py` — reads `co_*` attributes from `function.__code__` to infer JIT eligibility and dummy arg types
- `_compat.py` — version shims for differences between 3.13 and 3.14+

### Key constraints

- No native JIT control API exists in 3.13/3.14 — behavior is inferred or faked via warmup
- `_backend.py` is the single source of truth for version/JIT detection; nothing else branches on `sys.version_info`
- Must be a transparent no-op on non-JIT builds and non-CPython runtimes
- Do not suggest or use `sys.set_jit_level()` — it does not exist
