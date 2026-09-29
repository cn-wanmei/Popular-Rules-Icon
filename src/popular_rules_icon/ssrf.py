from __future__ import annotations

import ipaddress
import socket
from urllib.parse import urlparse


class SSRFError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.code = "SSRF_BLOCKED"


def assert_safe_url(url: str, *, allow_private: bool = False) -> None:
    parsed = urlparse(url)
    if parsed.scheme not in {"https"}:
        raise SSRFError(f"scheme not allowed: {parsed.scheme}")
    host = parsed.hostname
    if not host:
        raise SSRFError("missing host")
    if host in {"localhost", "metadata.google.internal"}:
        raise SSRFError(f"blocked host: {host}")
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror as exc:
        raise SSRFError(f"dns failed: {exc}") from exc
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if not allow_private and (
            ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved
        ):
            raise SSRFError(f"blocked ip: {ip}")
