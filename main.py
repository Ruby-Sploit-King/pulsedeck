import signal
import sys
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from pulsedeck.models import Service
from pulsedeck.probes import check_endpoint, validate_name, validate_url
from pulsedeck.registry import Registry
from pulsedeck.terminal_ui import (
    show_banner,
    show_history,
    show_message,
    show_result,
    show_services,
)

app = typer.Typer(
    name="pulsedeck",
    help="A neon terminal dashboard for HTTP service health.",
    no_args_is_help=False,
    add_completion=False,
)


@app.callback(invoke_without_command=True)
def dashboard(ctx: typer.Context) -> None:
    """Launch the PulseDeck dashboard when no command is given."""
    if ctx.invoked_subcommand is not None:
        return

    try:
        services = get_registry().list_services()
    except Exception as exc:
        show_banner()
        show_message(f"Could not load services: {exc}", "red")
        raise typer.Exit(code=1) from exc

    show_banner()

    if not services:
        show_message(
            "No services registered yet. Try 'PulseDeck add <name> <url>'.",
            "yellow",
        )
        return

    show_services(services)


def shutdown_handler(signum: int, frame: object) -> None:
    raise KeyboardInterrupt


def get_registry() -> Registry:
    return Registry()


def find_service(registry: Registry, name: str) -> Service:
    service = registry.get(validate_name(name))

    if service is None:
        raise ValueError(f"Service '{name}' was not found.")

    return service


@app.command()
def add(
    name: Annotated[str, typer.Argument(help="Unique service name.")],
    url: Annotated[str, typer.Argument(help="Absolute HTTP(S) URL.")],
) -> None:
    """Register a service for monitoring."""
    try:
        get_registry().add(validate_name(name), validate_url(url))
        show_message(f"Registered [bold]{name}[/bold].", "green")
    except ValueError as exc:
        show_message(str(exc), "red")
        raise typer.Exit(code=2) from exc
    except Exception as exc:
        show_message(f"Could not register service: {exc}", "red")
        raise typer.Exit(code=1) from exc


@app.command(name="list")
def list_services() -> None:
    """Display all registered services."""
    try:
        show_banner()
        show_services(get_registry().list_services())
    except Exception as exc:
        show_message(f"Could not load services: {exc}", "red")
        raise typer.Exit(code=1) from exc


@app.command()
def check(
    name: Annotated[
        str | None,
        typer.Argument(help="Optional service name; omit to check all."),
    ] = None,
    timeout: Annotated[
        float,
        typer.Option(
            "--timeout",
            min=0.1,
            max=60.0,
            help="Request timeout in seconds.",
        ),
    ] = 5.0,
) -> None:
    """Check one service or all registered services."""
    registry = get_registry()

    try:
        services = (
            [find_service(registry, name)]
            if name
            else registry.list_services()
        )
    except ValueError as exc:
        show_message(str(exc), "red")
        raise typer.Exit(code=2) from exc

    if not services:
        show_message("No services registered yet. Try 'pulsedeck add'.", "yellow")
        raise typer.Exit(code=0)

    failed = 0

    try:
        for service in services:
            result = check_endpoint(service.name, service.url, timeout)
            registry.record(result)
            show_result(result)
            failed += result.status != "UP"
    except KeyboardInterrupt:
        show_message("Check interrupted.", "yellow")
        raise typer.Exit(code=130) from None
    except Exception as exc:
        show_message(f"Check failed: {exc}", "red")
        raise typer.Exit(code=1) from exc

    if failed:
        raise typer.Exit(code=1)


@app.command()
def history(
    name: Annotated[str, typer.Argument(help="Service name.")],
    limit: Annotated[
        int,
        typer.Option("--limit", min=1, max=500, help="Maximum records."),
    ] = 20,
) -> None:
    """Show recent health checks."""
    try:
        registry = get_registry()
        find_service(registry, name)
        show_history(name, registry.history(name, limit))
    except ValueError as exc:
        show_message(str(exc), "red")
        raise typer.Exit(code=2) from exc


@app.command()
def remove(
    name: Annotated[str, typer.Argument(help="Service name.")],
    yes: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation."),
    ] = False,
) -> None:
    """Remove a service and its check history."""
    try:
        registry = get_registry()
        find_service(registry, name)

        if not yes and not typer.confirm(f"Remove '{name}' and its history?"):
            show_message("Removal cancelled.", "yellow")
            raise typer.Exit(code=0)

        registry.remove(name)
        show_message(f"Removed [bold]{name}[/bold].", "green")
    except ValueError as exc:
        show_message(str(exc), "red")
        raise typer.Exit(code=2) from exc


@app.command()
def export(
    output: Annotated[
        Path,
        typer.Argument(help="Destination JSON file."),
    ] = Path("reports/pulsedeck.json"),
) -> None:
    """Export services and check history as JSON."""
    try:
        get_registry().export_json(output)
        show_message(f"Exported report to {output}", "green")
    except (OSError, ValueError) as exc:
        show_message(f"Export failed: {exc}", "red")
        raise typer.Exit(code=1) from exc


def main() -> None:
    signal.signal(signal.SIGTERM, shutdown_handler)
    signal.signal(signal.SIGINT, shutdown_handler)
    try:
        app()
    except KeyboardInterrupt:
        Console(stderr=True).print("[yellow]PulseDeck stopped.[/yellow]")
        sys.exit(130)


if __name__ == "__main__":
    main()