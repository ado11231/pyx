class LoomError(Exception):
    """
    Default base exception for everything in this project
    all other exceptions inherit from this

    """
    pass

class PoolShutdownError(LoomError):
    """
    Error that is raised when a task is submitted after pool 
    has been closed.
    """
    pass

class InterpreterError(LoomError):
    """
    Error that is raised when something goes wrong inside a running subinterpreter
    """

    def __init__(self, interpreter_id, original_error):
        self.interpreter_id = interpreter_id
        self.original_error = original_error
        super().__init__(f"Interpreter {interpreter_id} failed {original_error}")
