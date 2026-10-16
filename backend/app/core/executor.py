"""Thread pool executor for running blocking calls asynchronously."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from functools import partial

# Global thread pool for Plex API calls
plex_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="plex")


def run_in_plex_executor(func, *args, **kwargs):
    """Run a function in the Plex thread pool executor.

    Args:
        func: The function to run.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        An awaitable that resolves to the function's return value.
    """
    loop = asyncio.get_event_loop()
    return loop.run_in_executor(plex_executor, partial(func, *args, **kwargs))