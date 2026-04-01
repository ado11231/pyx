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
    pass

