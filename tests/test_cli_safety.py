from typer.testing import CliRunner

from main import app


def test_help_displays_commands() -> None:
    result = CliRunner().invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "add" in result.output
    assert "check" in result.output
    assert "history" in result.output
    assert "export" in result.output


def test_missing_service_name_is_reported(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))

    result = CliRunner().invoke(app, ["check", "missing-service"])

    assert result.exit_code == 2
    assert "not found" in result.output.lower()