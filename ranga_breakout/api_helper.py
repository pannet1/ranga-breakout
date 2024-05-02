import time
import logging
import traceback
from functools import wraps


def retry(max_attempts):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(max_attempts):
                try:
                    resp = func(*args, **kwargs)
                    if isinstance(resp, dict):
                        if "data" not in resp:
                            raise Exception(f"no data in {resp}")
                        elif resp["data"] is None:
                            raise Exception("no value in resp data")
                    else:
                        raise Exception(f"unexpected {resp=} for {func.__name__}")
                    return resp["data"]
                except Exception as e:
                    print(f"While executing {func.__name__} {e}, Attempt {i+1}")
                    traceback.print_exc()
                    if i < max_attempts - 1:
                        time.sleep(i + 1)
                    else:
                        print(
                            f"Maximum retries {max_attempts} reached for {func.__name__}. Moving to the next operation."
                        )
                        break

        return wrapper

    return decorator


def run():
    @retry(max_attempts=3)
    def iterhere():
        print("entering run")
        # iterate from 0 to 2
        for i in range(3):
            t = i / 0
            print(f"{t=}")

    for j in range(2):
        print(j)
        iterhere()


if __name__ == "__main__":
    run()
