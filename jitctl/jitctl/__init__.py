# Public decorator API for jitctl
# @jit_focus  — hint that this function is hot and should be JIT-prioritized
# @jit_ignore — hint that this function should be excluded from JIT compilation
# @jit_once   — hint that this function should be compiled once and cached

def jit_focus(fn):
    raise NotImplementedError

def jit_ignore(fn):
    raise NotImplementedError

def jit_once(fn):
    raise NotImplementedError
