from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pulsedeck.models import CheckResult, Service

console = Console(stderr=False)

# --- Tokyo Night palette ---------------------------------------------------
TN_BG = "#1a1b26"
TN_BG_DARK = "#16161e"
TN_FG = "#c0caf5"
TN_FG_DARK = "#a9b1d6"
TN_COMMENT = "#565f89"
TN_BLUE = "#7aa2f7"
TN_CYAN = "#7dcfff"
TN_PURPLE = "#bb9af7"
TN_GREEN = "#9ece6a"
TN_RED = "#f7768e"
TN_ORANGE = "#ff9e64"
TN_YELLOW = "#e0af68"
TN_TEAL = "#73daca"
TN_BLACK = "#414868"

LOGO_GRADIENT = [TN_CYAN, TN_BLUE, TN_PURPLE, TN_RED]

PULSEDECK_LOGO = [
    r" ____  _   _ _     ____  _____ ",
    r"|  _ \| | | | |   / ___|| ____|",
    r"| |_) | | | | |   \___ \|  _|  ",
    r"|  __/| |_| | |___ ___) | |___ ",
    r"|_|    \___/|_____|____/|_____|",
    r"",
    r"     ____  _____ ____ _  __",
    r"    |  _ \| ____/ ___| |/ /",
    r"    | | | |  _|| |   | ' / ",
    r"    | |_| | |__| |___| . \ ",
    "    |____/|_____\\____|_|\\_\\",
]

BADGES = [
    ("build", "passing", TN_GREEN),
    ("version", "1.0.0", TN_BLUE),
    ("python", "3.11+", TN_YELLOW),
    ("license", "MIT", TN_PURPLE),
]


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def _sample_gradient(stops: list[str], position: float) -> str:
    position = min(max(position, 0.0), 1.0)
    scaled = position * (len(stops) - 1)
    index = min(int(scaled), len(stops) - 2)
    local = scaled - index
    start = _hex_to_rgb(stops[index])
    end = _hex_to_rgb(stops[index + 1])
    blended = (
        round(start[0] + (end[0] - start[0]) * local),
        round(start[1] + (end[1] - start[1]) * local),
        round(start[2] + (end[2] - start[2]) * local),
    )
    return _rgb_to_hex(blended)


def _gradient_logo(lines: list[str], stops: list[str]) -> Text:
    width = max((len(line) for line in lines), default=1)
    span = max(width - 1, 1)
    logo = Text()

    for row, line in enumerate(lines):
        for column, char in enumerate(line):
            if char == " ":
                logo.append(char)
                continue
            color = _sample_gradient(stops, column / span)
            logo.append(char, style=f"bold {color}")
        if row != len(lines) - 1:
            logo.append("\n")

    return logo


def _badge_row() -> Text:
    row = Text()

    for index, (label, value, color) in enumerate(BADGES):
        if index:
            row.append(" ")
        row.append(f" {label} ", style=f"{TN_FG} on {TN_BLACK}")
        row.append(f" {value} ", style=f"{TN_BG} on {color}")

    return row


def show_banner() -> None:
    content = Text()
    content.append_text(_gradient_logo(PULSEDECK_LOGO, LOGO_GRADIENT))
    content.append("\n\n")
    content.append_text(_badge_row())
    content.append("\n")
    content.append(
        "SERVICE HEALTH MONITOR  //  SYSTEM ONLINE",
        style=f"bold {TN_COMMENT}",
    )

    console.print(
        Panel(
            content,
            border_style=TN_BLUE,
            box=box.ROUNDED,
            padding=(1, 3),
        )
    )


def show_message(message: str, style: str = TN_CYAN) -> None:
    console.print(f"[{style}]◆[/{style}] {message}")


def show_services(services: list[Service]) -> None:
    table = Table(
        title="◈ REGISTERED SERVICES",
        box=box.ROUNDED,
        border_style=TN_BLUE,
        header_style=f"bold {TN_CYAN}",
        title_style=f"bold {TN_PURPLE}",
    )
    table.add_column("SERVICE", style=f"bold {TN_FG}")
    table.add_column("STATUS", justify="center")
    table.add_column("LATENCY", justify="right", style=TN_TEAL)
    table.add_column("URL", style=TN_FG_DARK, overflow="fold")
    table.add_column("LAST CHECKED", style=TN_COMMENT, overflow="fold")

    for service in services:
        color = {"UP": TN_GREEN, "DOWN": TN_RED}.get(
            service.last_status, TN_YELLOW
        )
        latency = (
            f"{service.last_latency_ms:.1f} ms"
            if service.last_latency_ms is not None
            else "—"
        )
        checked = service.last_checked_at or "Never"
        table.add_row(
            service.name,
            f"[bold {color}]● {service.last_status}[/bold {color}]",
            latency,
            service.url,
            checked,
        )

    console.print(table)
    up = sum(service.last_status == "UP" for service in services)
    down = sum(service.last_status == "DOWN" for service in services)
    console.print(
        f"[{TN_GREEN}]● {up} UP[/]  "
        f"[{TN_RED}]● {down} DOWN[/]  "
        f"[{TN_COMMENT}]◈ {len(services)} TOTAL[/]"
    )


def show_result(result: CheckResult) -> None:
    color = TN_GREEN if result.status == "UP" else TN_RED
    code = result.status_code if result.status_code is not None else "—"
    console.print(
        f"[bold {color}]{result.status}[/bold {color}] "
        f"[{TN_FG}]{result.name}[/]  "
        f"[{TN_TEAL}]{result.latency_ms:.1f} ms[/]  "
        f"[{TN_COMMENT}]HTTP {code} · {result.message}[/]"
    )


def show_history(name: str, entries: list[dict[str, object]]) -> None:
    table = Table(
        title=f"◈ HISTORY / {name}",
        box=box.ROUNDED,
        border_style=TN_PURPLE,
        header_style=f"bold {TN_CYAN}",
        title_style=f"bold {TN_PURPLE}",
    )
    table.add_column("TIME", style=TN_COMMENT)
    table.add_column("STATUS")
    table.add_column("HTTP", justify="right", style=TN_FG_DARK)
    table.add_column("LATENCY", justify="right", style=TN_TEAL)
    table.add_column("MESSAGE", style=TN_FG_DARK, overflow="fold")

    for entry in entries:
        status = str(entry["status"])
        color = TN_GREEN if status == "UP" else TN_RED
        code = entry["status_code"] or "—"
        table.add_row(
            str(entry["checked_at"]),
            f"[bold {color}]{status}[/bold {color}]",
            str(code),
            f"{entry['latency_ms']} ms",
            str(entry["message"]),
        )

    console.print(table)
