import asyncio
import sys

def get_event_loop():
    """Returns a new event loop appropriate for the platform."""
    if sys.platform.startswith('win'):
        return asyncio.ProactorEventLoop()
    return asyncio.new_event_loop()

def run_async_task(coro):
    """Runs an async coroutine synchronously using a new event loop."""
    loop = get_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
