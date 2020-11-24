import inspect
import logging
from functools import wraps


def _execute_function(func, arguments, *args, **kwargs):
    path = f'{inspect.getmodule(func).__name__}.{func.__name__}'
    logging.info(f'Executing Function: ({path})')
    if arguments:
        arg_string = ', '.join([f'{args[value]}' for value in arguments])
        kw_arg_string = ', '.join([f'{arg}={value}' for arg, value in kwargs.items() if arg in arguments])
        if kw_arg_string:
            arg_string = f'{arg_string}, {kw_arg_string}'
        logging.info(f'Executing with arguments: ({arg_string})')
    try:
        result = func(*args, **kwargs)
    except:
        logging.exception(f'Exception occurred during runtime')
        raise
    if result:
        logging.info(f'{func.__name__}() successfully executed, returning {type(result)} {result}')
    return result


def event(arguments: list = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return _execute_function(func, arguments, *args, **kwargs)

        return wrapper

    return decorator
