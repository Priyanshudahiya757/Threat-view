"""Shared HTTP session factory for the ingestors.

Centralizes retry/backoff behavior so every feed integration gets the
same resilience without each ingestor re-implementing it.
"""
import logging

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


def build_http_session(
    retries: int = 3,
    backoff_factor: float = 0.5,
    status_forcelist=(429, 500, 502, 503, 504),
) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
        allowed_methods=("GET", "POST"),
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session