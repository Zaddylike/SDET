import base64, json, logging, time



# try-except decorator

def try_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error occurred: {e}", exc_info=True)
        return result
    return wrapper

#  Regiter the patterns

def register_pattern(sometging_pattern,method):
    def wrapper(func):
        sometging_pattern[method] = func
        return func
    return wrapper

#  count time
def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logging.info(f"running time: {end-start:.4f}s")
        return result 