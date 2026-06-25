"""
cit411_utils.net
----------------
HTTP utilities: fetching URLs with retry logic.

Note: parse_headers() is intentionally private (_parse_headers) as of v1.1.0.
It supports fetch_url internally but has no standalone use case for callers.
"""

import time
import urllib.error
import urllib.request


def fetch_url(
    url: str,
    *,
    timeout: int = 10,
    retries: int = 2,
    headers: "dict | None" = None,
) -> str:
    """
    Fetch the text body of *url* via HTTP GET.

    Retries up to *retries* times on transient network errors,
    with a brief exponential back-off between attempts.

    Parameters
    ----------
    url     : str
        Fully-qualified HTTP/HTTPS URL.
    timeout : int, default 10
        Per-attempt timeout in seconds.
    retries : int, default 2
        Number of retry attempts after the first failure.
    headers : dict | None, default None
        Additional request headers (e.g. ``{"User-Agent": "cit411/1.0"}``).

    Returns
    -------
    str
        Decoded response body (UTF-8).

    Raises
    ------
    urllib.error.URLError
        On unrecoverable failure after all retries are exhausted.

    Examples
    --------
    >>> body = fetch_url("https://httpbin.org/get")
    >>> "url" in body
    True
    """
    req = urllib.request.Request(url, headers=headers or {})
    last_error = None

    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8")
        except urllib.error.URLError as exc:
            last_error = exc
            if attempt < retries:
                time.sleep(2 ** attempt)  # 1s, 2s, ...

    raise last_error


# ── Private helper (not exported) ────────────────────────────────────────
def _parse_headers(raw: str) -> "dict[str, str]":
    """
    Parse a raw HTTP header block into a case-normalised dict.

    Private as of v1.1.0: only used internally by fetch_url's test fixtures.
    Accepts both CRLF (\\r\\n) and LF (\\n) line endings.
    Header names are lowercased; values are stripped of whitespace.

    Parameters
    ----------
    raw : str
        Raw header string, e.g. from a socket or test fixture.

    Returns
    -------
    dict[str, str]
        {lowercase-header-name: value}

    Examples
    --------
    >>> _parse_headers("Content-Type: text/html\\r\\nX-Foo: bar")
    {'content-type': 'text/html', 'x-foo': 'bar'}
    """
    result = {}
    for line in raw.splitlines():
        line = line.strip()
        if ":" in line:
            name, _, value = line.partition(":")
            result[name.strip().lower()] = value.strip()
    return result
