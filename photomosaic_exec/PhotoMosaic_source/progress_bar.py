"""
progress_bar.py

PURPOSE:
    Implements a generator function for logging progress during long-running operations (like tile analysis or mosaic assembly).

HOW IT COMMUNICATES:
    - Logs progress to the logger configured in the calling code.
    - No file, DB, or network I/O.

PATHS TO CHECK:
    - No paths to configure.

MODERNIZATION NOTES:
    - Uses time.perf_counter() (Python 3.3+), which is recommended for measuring elapsed time.
    - All other code is portable.
"""

import logging
import time

logger = logging.getLogger(__name__)

def progress_bar(total_steps, message=''):
    """
    Generator for progress logging during long operations.

    Usage:
        pbar = progress_bar(len(steps), "Processing tiles")
        for step in steps:
            ...
            next(pbar)

    Args:
        total_steps (int): The total number of steps in the task.
        message (str): Optional start message for the log.

    Yields:
        None
    """
    logger.info('%s...', message)
    step = 0
    start = time.perf_counter()
    previous_notif = start
    virgin = True

    while step < total_steps - 1:
        now = time.perf_counter()
        elapsed = now - start
        if (now - previous_notif) > 10:
            logger.info("%.2f %% completed after %d seconds elapsed",
                        100 * (step / total_steps), round(elapsed))
            previous_notif = now
        elif virgin and elapsed > 1:
            virgin = False
            logger.info("%.2f %% completed after %d second elapsed",
                        100 * (step / total_steps), round(elapsed))
        yield
        step += 1
    logger.info("100 %% completed in %d seconds.", round(time.perf_counter() - start))
    yield