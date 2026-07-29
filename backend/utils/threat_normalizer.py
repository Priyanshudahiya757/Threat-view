"""Helpers for deriving host-level indicators from URLs."""
import ipaddress
from typing import Optional, Tuple
from urllib.parse import urlparse


def classify_host(host: str) -> str:
    try:
        ipaddress.ip_address(host)
        return "IP"
    except ValueError:
        return "Domain"


def extract_host_indicator(url: str) -> Optional[Tuple[str, str]]:
    try:
        host = urlparse(url).hostname
    except ValueError:
        return None
    if not host:
        return None
    return host, classify_host(host)