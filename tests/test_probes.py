from email.message import Message
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import pytest

from pulsedeck.probes import check_endpoint, validate_name, validate_url


@pytest.mark.parametrize(
    "name",
    ["", " ", "../private", "name with spaces", "x" * 65],
)
def test_invalid_names_are_rejected(name: str) -> None:
    with pytest.raises(ValueError):
        validate_name(name)


def test_valid_name_is_trimmed() -> None:
    assert validate_name("  homepage  ") == "homepage"


@pytest.mark.parametrize(
    "url",
    [
        "ftp://example.com",
        "example.com",
        "https://user:secret@example.com",
        "https://example.com:invalid",
    ],
)
def test_invalid_urls_are_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        validate_url(url)


def test_valid_url_is_trimmed() -> None:
    assert validate_url(" https://example.com ") == "https://example.com"


@patch("pulsedeck.probes.urlopen")
def test_successful_check_returns_up(mock_urlopen: MagicMock) -> None:
    response = MagicMock()
    response.status = 200
    response.__enter__.return_value = response
    mock_urlopen.return_value = response

    result = check_endpoint("homepage", "https://example.com")

    assert result.status == "UP"
    assert result.status_code == 200
    assert result.latency_ms >= 0


@patch("pulsedeck.probes.urlopen")
def test_http_error_returns_down(mock_urlopen: MagicMock) -> None:
    mock_urlopen.side_effect = HTTPError(
        "https://example.com",
        503,
        "Service unavailable",
        Message(),
        None,
    )

    result = check_endpoint("api", "https://example.com")

    assert result.status == "DOWN"
    assert result.status_code == 503


@patch("pulsedeck.probes.urlopen")
def test_network_failure_returns_down(mock_urlopen: MagicMock) -> None:
    mock_urlopen.side_effect = TimeoutError("Timed out")

    result = check_endpoint("api", "https://example.com")

    assert result.status == "DOWN"
    assert result.status_code is None