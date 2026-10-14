from time import monotonic
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from pulsedeck.models import CheckResult


def validate_name(name: str) -> str:
    cleaned = name.strip()

    if not cleaned or len(cleaned) > 64:
        raise ValueError("Name must contain 1-64 characters.")

    if not all(char.isalnum() or char in "-_." for char in cleaned):
        raise ValueError("Use only letters, numbers, dots, dashes, underscores.")

    return cleaned 

def validate_url(url: str) -> str:
    cleaned = url.strip()

    try:
        parsed = urlsplit(cleaned)
        port = parsed.port 
    except ValueError as exc:
        raise ValueError("URL contains an invalid port or address.") from exc 

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("URL must start with http:// or https://")

    if not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("URL must have a hostname and no embedded credentials.")

    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Port must be between 1 and 65535.")

    return cleaned 

def check_endpoint(
    name: str,
    url: str,
    timeout: float = 5.0,
) -> CheckResult:
    request = Request(
        url,
        headers={"User-Agent": "PulseDeck/1.0"},
        method="GET",
    )
    started = monotonic()

    try:
        with urlopen(request, timeout=timeout) as response:
            code = response.status
            status = "UP" if 200 <= code < 400 else "DOWN"
            message = "HTTP response received"
    except HTTPError as exc:
        code = exc.code
        status = "UP" if 200 <= code < 400 else "DOWN"
        message = f"HTTP {code}"
    except (URLError, TimeoutError, OSError, ValueError) as exc:
        code = None
        status = "DOWN"
        message = str(getattr(exc, "reason", exc))[:200]

    latency = (monotonic() - started) * 1000

    return CheckResult.create(
        name=name,
        url=url,
        status=status,
        status_code=code,
        latency_ms=latency,
        message=message,
    )