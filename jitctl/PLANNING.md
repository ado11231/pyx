# jitctl — Design & Planning Doc

## What it is

A Python library that gives developers **hint-based control** over CPython's JIT compiler via decorators. The public API is stable today; the backend strategies evolve as CPython exposes more native JIT control.

## The core problem

CPython 3.13 introduced an experimental JIT (copy-and-patch). Python 3.14 continues that work. But as of now, **no public per-function API exists** to tell the JIT what to prioritize, skip, or cache. Developers have no knobs.

`jitctl` bridges that gap with a stable decorator API that works today through inference and warm-up tricks, and will transparently upgrade to native hooks when CPython exposes them.

---

## Public API (three decorators)

```python
@jit_focus   # I think this function is hot — do your best to JIT it
@jit_ignore  # Don't bother JIT-ing this — it's cold, infrequent, or has side effects
@jit_once    # JIT it, but don't re-specialize — I call it with many different types
```

These are the only things users import. Everything else is internal.

### Design question to settle before implementing
- Should the decorators be **no-ops that return the original function** on non-JIT builds, or should they always apply the warmup strategy? Leaning toward: always apply strategy (warmup is useful even without JIT), but gate any introspection/profiling overhead behind a JIT-detected build.

---

## Internal architecture

### `_backend.py` — the version router (implement this first)

This is the heart of the library. It does two things:

1. **Detects the Python version and JIT availability** at import time using `sys.version_info` and checking for JIT-specific attributes (e.g. `sys._jit_enabled()` if/when that lands, or inspecting `sys.flags`).
2. **Returns the right strategy object** for a given decorator. Today that's always the warmup strategy. In future Python versions it could be a native hook.

```
_backend.get_strategy("focus")  → WarmupStrategy | NativeJITStrategy
```

The rest of the codebase never checks the Python version directly — it always asks `_backend`.

#### Future hook points to watch
- CPython issue tracker: bpo/gh issues around `sys.set_jit_level()` or per-function JIT control
- `sys._jit_enabled()` — rumored, not confirmed in 3.14 yet
- `code.co_qualname` and `code.co_flags` changes that might signal JIT tier

### `_warmup.py` — today's main strategy

Warm-up works by calling the function N times with synthetic/dummy arguments before returning it to the caller. This causes CPython's specializing adaptive interpreter to tier up the bytecode faster.

#### Key design questions
- **How many warmup iterations?** CPython's threshold to tier-1 specialization is around 8–16 calls; tier-2 (actual JIT) is higher (~100). Need to benchmark. Start with a configurable default (e.g. 50).
- **What dummy args to use?** This is the hard part. Options:
  - Inspect the function signature and generate typed defaults (`int` → `0`, `str` → `""`, etc.) using `inspect.signature()` + `_introspect.py`.
  - Require the user to pass `sample_args` to the decorator: `@jit_focus(sample_args=(1, 2))`.
  - Call with no args and catch `TypeError` silently. Simple but unreliable.
  - Recommendation: start with `sample_args` as an optional parameter; fall back to no-arg call.
- **When does warmup run?** Options: at decoration time (module load), at first call, or lazily after N real calls. At decoration time is simplest but can slow imports.

### `_profiler.py` — call counting and timing

Wraps the function to track:
- How many times it's been called
- Average/min/max execution time

Used by `@jit_focus` to verify the warmup actually had an effect, and potentially to feed adaptive decisions (e.g. re-warm if performance degrades, which might indicate de-optimization).

Also useful for a future `jitctl.stats()` public API that lets developers inspect what the library actually did.

### `_introspect.py` — code object inspection

CPython exposes a `function.__code__` object (a `code` object) with attributes like:
- `co_argcount` — number of positional args
- `co_varnames` — local variable names
- `co_flags` — bitmask of compiler flags
- `co_consts`, `co_names` — constants and global names referenced

Use this to:
- Infer argument types for warmup dummy args
- Detect functions that are likely JIT-unfriendly (e.g. those that use `eval`, `exec`, or dynamic `__code__` replacement)
- Check if a function is already "warm" before doing unnecessary warmup

This is the most exploratory module — read CPython docs and source on `code` objects before implementing.

### `_compat.py` — version shims

Single place to normalize anything that changed between 3.13 and 3.14+. Examples:
- If a new `sys` attribute appears in 3.14, access it here with a fallback for 3.13.
- Any bytecode-level differences relevant to JIT tier detection.

Keep this minimal — only add a shim when a real divergence is found.

---

## Build order (when ready to implement)

1. `_compat.py` — trivial, just `sys.version_info` checks
2. `_backend.py` — version detection + strategy interface (no real strategies yet, just stubs)
3. `_introspect.py` — read `co_*` attributes, no side effects, easy to test in isolation
4. `_profiler.py` — simple wrapper, no JIT knowledge needed
5. `_warmup.py` — depends on `_introspect.py` for dummy arg inference
6. `__init__.py` — wire up decorators through `_backend.py`

---

## Graceful degradation rules

- On a non-JIT CPython build (e.g. regular 3.13 without `--enable-experimental-jit`): decorators should be **transparent no-ops** — return the original function unchanged, zero overhead.
- On PyPy or other non-CPython: same — no-ops.
- On a JIT-enabled build with no native hook API: apply warmup strategy.
- On a future build with native JIT hooks: use them via `_backend.py`.

This means `_backend.py` must detect **both** "is this CPython?" and "is JIT enabled?" before doing anything.

---

## Open questions (resolve before implementing)

1. Should `@jit_once` actually suppress re-specialization, or just warm up once and add a profiler guard that skips re-warmup? There is no CPython API today to prevent re-specialization.
2. Should the library expose a `jitctl.stats()` function that prints what each decorated function did? Useful for debugging, but adds surface area.
3. Should warmup happen at decoration time or first call? This affects import performance.
4. What's the `sample_args` UX? `@jit_focus(sample_args=(1, 2))` vs `@jit_focus` with auto-inference?
