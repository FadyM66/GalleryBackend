import logging
import inspect
import linecache
from functools import wraps

logger = logging.getLogger('django')

def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            frame = inspect.currentframe().f_back
            line_number = frame.f_lineno
            code_line = linecache.getline(frame.f_code.co_filename, line_number).strip()

            logger.error(f"Error: {e}, occurred at line {line_number} - {code_line}")

            print(f"Error: {e}, occurred at line {line_number} - {code_line}")
            return None
    return wrapper
