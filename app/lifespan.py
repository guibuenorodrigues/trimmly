import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import settings
from app.logger import logger
from app.services.kgs import fill_key_pool
from app.services.metrics import metrics_queue, metrics_worker

# Our worker task variable, so we can cancel it later
metrics_worker_task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up application...")

    fill_key_pool(pool_size=settings.KGS_KEY_POOL_SIZE)

    global metrics_worker_task
    metrics_worker_task = asyncio.create_task(metrics_worker())

    yield

    logger.info("Shutting down application...")

    await metrics_queue.put(None)  # Signal the worker to exit
    logger.info("Sent shutdown signal to metrics worker.")
    await metrics_queue.join()  # Wait until all tasks are processed
    logger.info("Metrics queue has been fully processed.")
    metrics_worker_task.cancel()

    # Wait for the task to be cancelled.
    try:
        logger.info("Waiting for worker task to be cancelled...")
        await metrics_worker_task
    except asyncio.CancelledError:
        logger.info("Worker task cancelled successfully.")
    except Exception as e:
        logger.warning(f"Exception during worker task cancellation: {e}")
