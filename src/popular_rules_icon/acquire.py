from __future__ import annotations

import urllib.error
import urllib.request
from dataclasses import dataclass

from .ssrf import SSRFError, assert_safe_url


@dataclass
class FetchResult:
    ok: bool
    data: bytes | None = None
    status: int | None = None
    etag: str | None = None
    last_modified: str | None = None
    content_type: str | None = None
    failure_code: str | None = None
    error: str | None = None


def fetch_url(
    url: str,
    *,
    timeout: float = 15.0,
    max_bytes: int = 5_242_880,
    etag: str | None = None,
    last_modified: str | None = None,
    allow_private: bool = False,
) -> FetchResult:
    try:
        assert_safe_url(url, allow_private=allow_private)
    except SSRFError as exc:
        return FetchResult(ok=False, failure_code=exc.code, error=str(exc))

    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "Mozilla/5.0 (compatible; Popular-Rules-Icon/0.1)"})
    if etag:
        req.add_header("If-None-Match", etag)
    if last_modified:
        req.add_header("If-Modified-Since", last_modified)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)
            data = resp.read(max_bytes + 1)
            if len(data) > max_bytes:
                return FetchResult(ok=False, status=status, failure_code="QUALITY_FAIL", error="too large")
            return FetchResult(
                ok=True,
                data=data,
                status=status,
                etag=resp.headers.get("ETag"),
                last_modified=resp.headers.get("Last-Modified"),
                content_type=resp.headers.get("Content-Type"),
            )
    except urllib.error.HTTPError as exc:
        if exc.code == 304:
            return FetchResult(ok=True, status=304, etag=etag, last_modified=last_modified)
        code = "SOURCE_404" if exc.code == 404 else "UNKNOWN"
        return FetchResult(ok=False, status=exc.code, failure_code=code, error=str(exc))
    except TimeoutError:
        return FetchResult(ok=False, failure_code="SOURCE_TIMEOUT", error="timeout")
    except Exception as exc:  # noqa: BLE001
        return FetchResult(ok=False, failure_code="UNKNOWN", error=str(exc))
