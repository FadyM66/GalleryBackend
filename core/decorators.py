import logging
import inspect
import asyncio
from functools import wraps

logger = logging.getLogger('django')

def error_handler(func):
    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            frame = e.__traceback__.tb_frame
            line_number = e.__traceback__.tb_lineno
            line_of_code = inspect.getsource(frame).strip()
            logger.error(f"Error occurred in {func.__name__} at line {line_number}: {line_of_code} - {e}", exc_info=True)
            return {"errorMessage": str(e)}
    
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            frame = e.__traceback__.tb_frame
            line_number = e.__traceback__.tb_lineno
            line_of_code = inspect.getsource(frame).strip()
            logger.error(f"Error occurred in {func.__name__} at line {line_number}: {line_of_code} - {e}", exc_info=True)
            return {"errorMessage": str(e)}

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
