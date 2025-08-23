import asyncio

from app.logger import logger

metrics_queue: asyncio.Queue = asyncio.Queue()


async def metrics_worker():
    """
    A dedicated worker that processes tasks from the queue until a None
    sentinel is received, signaling shutdown.
    """

    logger.info("Metrics worker started.")

    while True:
        task = await metrics_queue.get()
        if task is None:
            metrics_queue.task_done()
            break

        try:
            await task()
        except Exception as e:
            logger.error(f"Error processing metrics task: {e}")
        finally:
            metrics_queue.task_done()

    logger.info("Metrics worker stopped.")
