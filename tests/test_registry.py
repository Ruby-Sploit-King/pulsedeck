from pathlib import Path
from typing import cast

from pulsedeck.models import CheckResult
from pulsedeck.registry import Registry


def test_service_lifecycle_and_history(tmp_path: Path) -> None:
    registry = Registry(tmp_path / "test.db")
    registry.add("homepage", "https://example.com")

    service = registry.get("homepage")

    assert service is not None
    assert service.url == "https://example.com"
    assert service.last_status == "UNKNOWN"

    result = CheckResult.create(
        "homepage",
        "https://example.com",
        "UP",
        200,
        25.0,
        "HTTP response received",
    )
    registry.record(result)

    updated = registry.get("homepage")

    assert updated is not None
    assert updated.last_status == "UP"
    assert len(registry.history("homepage")) == 1

    assert registry.remove("homepage") is True
    assert registry.get("homepage") is None
    assert registry.history("homepage") == []


def test_duplicate_service_names_are_rejected(tmp_path: Path) -> None:
    registry = Registry(tmp_path / "test.db")
    registry.add("homepage", "https://example.com")

    try:
        registry.add("homepage", "https://another.example")
    except Exception:
        pass
    else:
        raise AssertionError("Expected duplicate name to fail")


def test_export_contains_services_and_checks(tmp_path: Path) -> None:
    registry = Registry(tmp_path / "test.db")
    registry.add("api", "https://example.com/api")
    result = CheckResult.create(
        "api",
        "https://example.com/api",
        "UP",
        200,
        8.0,
        "OK",
    )
    registry.record(result)

    exported = registry.export_data()

    assert len(cast(list[object], exported["services"])) == 1
    assert len(cast(list[object], exported["checks"])) == 1