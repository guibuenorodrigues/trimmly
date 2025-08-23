import queue
import secrets
import string

from app.logger import logger

keys_queue = queue.Queue()

BASE62_CHARS = string.digits + string.ascii_letters


def generate_key(length: int = 7) -> str:
    return "".join(secrets.choice(BASE62_CHARS) for _ in range(length))


def fill_key_pool(pool_size: int = 100) -> set[str]:
    while keys_queue.qsize() < pool_size:
        key = generate_key()
        keys_queue.put(key)
    logger.info(f"Key pool filled. Current size: {keys_queue.qsize()}")
    return set(keys_queue.queue)


def get_next_key() -> str:
    if keys_queue.empty():
        fill_key_pool()
    key = keys_queue.get(timeout=1)
    keys_queue.task_done()
    return key


def validate_key_uniqueness(key: str) -> bool:
    return key not in keys_queue.queue


def validate_custom_key(key: str) -> tuple[bool, str]:
    if len(key) < 1 or len(key) > 8:
        return False, "Invalid length"
    if not all(c in BASE62_CHARS for c in key):
        return False, "Invalid characters"
    if not validate_key_uniqueness(key):
        return False, "Key already exists"
    return True, ""


if __name__ == "__main__":
    fill_key_pool()
    print(f"Generated {len(keys_queue.queue)} keys.")
    print(f"Random key: {secrets.choice(list(keys_queue.queue))}")
