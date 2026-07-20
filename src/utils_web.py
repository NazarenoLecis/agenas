"""
Utility web semplici per discovery e validazione di fonti pubbliche.
"""

from urllib.parse import urlparse, urldefrag
import requests
from bs4 import BeautifulSoup


DEFAULT_HEADERS = {"User-Agent": "Agenas-data-analysis/0.1"}
REQUEST_TIMEOUT_SECONDS = 10
SKIP_SCHEMES = {"mailto", "tel", "javascript", "data"}


def is_http_url(url):
    return urlparse(str(url)).scheme in {"http", "https"}


def normalize_url(url):
    if not isinstance(url, str) or not url:
        return ""
    cleaned, _ = urldefrag(url.strip())
    return cleaned


def should_skip_href(href):
    if not href:
        return True
    return urlparse(href).scheme in SKIP_SCHEMES


def get_public_url(url, params=None, timeout_seconds=REQUEST_TIMEOUT_SECONDS, stream=False):
    return requests.get(
        url,
        params=params or {},
        headers=DEFAULT_HEADERS,
        timeout=timeout_seconds,
        allow_redirects=True,
        stream=stream,
    )


def head_public_url(url, timeout_seconds=REQUEST_TIMEOUT_SECONDS):
    return requests.head(url, headers=DEFAULT_HEADERS, timeout=timeout_seconds, allow_redirects=True)


def parse_html(html):
    return BeautifulSoup(html, "lxml")
