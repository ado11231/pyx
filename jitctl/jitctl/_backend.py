# Version detection and strategy routing — the only module that knows which Python version is running.
# Routes decorator calls to the correct strategy: warmup-loop (3.13/3.14 today),
# or native JIT hooks when CPython exposes them in a future version.
