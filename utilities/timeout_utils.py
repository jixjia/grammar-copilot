import threading

class TimeoutError(Exception):
    pass

def with_timeout(timeout_seconds):
    def decorator(func):
        def wrapper(*args, **kwargs):
            result = [None]  # Use a mutable object to store the result

            def target():
                result[0] = func(*args, **kwargs)

            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout_seconds)

            if thread.is_alive():
                thread.join()  # Wait for the thread to finish
                raise TimeoutError("timeout")

            return result[0]
        return wrapper
    return decorator
