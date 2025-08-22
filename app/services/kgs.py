import secrets
import string

BASE62_CHARS = string.digits + string.ascii_letters

keys_cache = set[str]()


def generate_key(length: int = 7) -> str:
    return "".join(secrets.choice(BASE62_CHARS) for _ in range(length))


def fill_key_pool(pool_size: int = 100) -> set[str]:
    while len(keys_cache) < pool_size:
        keys_cache.add(generate_key())
    return keys_cache


def get_next_key() -> str:
    if not keys_cache:
        fill_key_pool()
    return keys_cache.pop()


def validate_key_uniqueness(key: str) -> bool:
    return key not in keys_cache


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
    print(f"Generated {len(keys_cache)} keys.")
    print(f"Random key: {secrets.choice(list(keys_cache))}")
