from pulsedeck.models import CheckResult


def test_check_result_rounds_latency() -> None:
    result = CheckResult.create(
        "homepage",
        "https://example.com",
        "UP",
        200,
        12.3456,
        "HTTP response received",
    )

    assert result.latency_ms == 12.35
    assert result.status == "UP"


def test_check_result_exports_json_compatible_data() -> None:
    result = CheckResult.create(
        "api",
        "https://example.com/api",
        "DOWN",
        None,
        10.0,
        "Timeout",
    )

    exported = result.to_dict()

    assert exported["name"] == "api"
    assert exported["status_code"] is None
    assert isinstance(exported["checked_at"], str)