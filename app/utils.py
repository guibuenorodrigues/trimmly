from urllib.parse import urlparse

import requests

from app.logger import logger


def smart_url_schema_detection(url: str) -> str:
    if not url:
        raise ValueError("Invalid URL")

    parsed_url = urlparse(url)

    if parsed_url.scheme in ("http", "https"):
        return url

    base_url = url
    https_url = "https://" + base_url
    if test_url_availability(https_url):
        return https_url

    # fallback to http
    http_url = "http://" + base_url
    if test_url_availability(http_url):
        return http_url

    # If both fail, default to HTTPS (let the redirect handle the error)
    logger.warning(f"Could not verify connectivity for {url}, defaulting to HTTPS")
    return https_url


def test_url_availability(url: str, timeout: int = 3):
    try:
        response = requests.head(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": "URL-Shortener-Trimmly/1.0"},
        )
        return response.status_code < 400
    except (requests.Timeout, requests.RequestException):
        return False
