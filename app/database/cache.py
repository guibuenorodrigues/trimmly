from app.models.url import URLMapping

_cached_urls: dict[str, URLMapping] = {}


def set_url_value(short_key: str, url_mapping: URLMapping) -> None:
    _cached_urls[short_key] = url_mapping


def get_url_value(short_key: str) -> URLMapping | None:
    return _cached_urls.get(short_key)


def clear_url_cache(short_key: str) -> None:
    _cached_urls.pop(short_key, None)


def reset_url_cache() -> None:
    _cached_urls.clear()
