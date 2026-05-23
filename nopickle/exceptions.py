# Nopickle-specific exceptions

class NopickleError(Exception):
    pass

class PoolShutdownError(NopickleError):
    pass

class InterpreterError(NopickleError):
    def __init__(self, interpreter_id, original_error):
        self.interpreter_id = interpreter_id
        self.original_error = original_error
        super().__init__(f"Interpreter {interpreter_id} failed: {original_error}")
