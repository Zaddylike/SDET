#  internal  function

#  internal parameter

#  external function and parameter
from functools import wraps
import logging
import asyncio
import time

#  try-except decorator

def try_wrapper(log_msg=None):
    def decorator(func):

        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"{log_msg or func.__name__}: {e}", exc_info=True)
                    raise
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"{log_msg or func.__name__}: {e}", exc_info=True)
                    raise
            return sync_wrapper
        
    return decorator

# lock the function

def lock_with(lock_name):
    def decorator(func):
        @wraps(func)
        async def async_lock(*args, **kwargs):
            async with lock_name:
                return await func(*args, **kwargs)
        return async_lock
    return decorator


#  register some pattern

def register_pattern(sometging_pattern,method):
    def wrapper(func):
        sometging_pattern[method] = func
        return func
    return wrapper

#  count time for wbsk

def wbsk_timer(func):
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        status, reps = await func(*args, **kwargs)
        end = time.perf_counter()
        return status, reps
    return wrapper