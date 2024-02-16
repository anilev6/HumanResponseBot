import logging
from logging import handlers

import asyncio
import sys
import os
import time

import re
import functools

NAME = "LanguageQuizFirst.log"

os.environ["PYTHONIOENCODING"] = "utf-8"

# --------------------------------------UTILS-----------------------------------------------
def redacted(error_msg: str) -> str:
    """this is a filter function for errors to cover unnecessary info"""
    error_msg = re.sub(r"api-\w{4}-\w{4}-\w{4}", "[REDACTED-API-KEY]", error_msg)
    error_msg = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b",
        "[REDACTED-EMAIL]",
        error_msg,
    )
    error_msg = re.sub(r"(https://api.telegram.org/).*", r"\1 [REDACTED]", error_msg)
    return error_msg


# -------------------------------------SET UP-----------------------------------------------
class CustomStreamHandler(logging.StreamHandler):
    def __init__(self, stream=sys.stdout):
        super().__init__(stream=stream)

    def emit(self, record):
        try:
            msg = self.format(record)
            # Encode and directly write bytes to the underlying buffer of the stream
            # if it's available (this bypasses the encoding issues of the stream's write method)
            if hasattr(self.stream, "buffer"):
                self.stream.buffer.write(
                    msg.encode("utf-8") + self.terminator.encode("utf-8")
                )
            else:
                # Fallback to writing as a string if buffer is not available
                self.stream.write(msg + self.terminator)
            self.flush()
        except Exception:
            self.handleError(record)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        CustomStreamHandler(),
        # automatic log rotation
        handlers.RotatingFileHandler(NAME, maxBytes=2 * 1024 * 1024, backupCount=5),
    ],
)

# get rid of the annoying logs
logging.getLogger("http").propagate = False
logging.getLogger("httpx").propagate = False
logging.getLogger("aiohttp").propagate = False

logger = logging.getLogger(__name__)


# -----------------------------------UNIVERSAL DEBUG DECORATOR--------------------------------
def time_log_decorator(func):
    if asyncio.iscoroutinefunction(func):

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            logger.info(f"Entering {func.__name__}")

            try:
                result = await func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {redacted(str(e))}")
                raise e

            else:
                elapsed_time = time.time() - start_time
                logger.info(
                    f"Exiting {func.__name__}. Execution time: {elapsed_time:.4f} seconds"
                )
                return result

        return async_wrapper
    else:

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            logger.info(f"Entering {func.__name__}")

            try:
                result = func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {redacted(str(e))}")
                raise e
            else:
                elapsed_time = time.time() - start_time
                logger.info(
                    f"Exiting {func.__name__}. Execution time: {elapsed_time:.4f} seconds"
                )
                return result

        return wrapper


# -----------------------------------------TEST DECORATOR-----------------------------------
@time_log_decorator
def test_function():
    print("Inside a synchronous function")


@time_log_decorator
async def async_test_function():
    print("Entering an asynchronous function")
    await asyncio.sleep(1)
    print("Exiting an asynchronous function")


# Test the decorator
if __name__ == "__main__":
    test_function()
    asyncio.run(async_test_function())
