<div align="center">

# PulseDeck

**A neon terminal dashboard for HTTP service health.**

Register services under short names, probe them over HTTP(S), track status and
latency history in a persistent SQLite registry, and export the deck to JSON.

[![CI](https://github.com/Ruby-Sploit-King/pulsedeck/actions/workflows/ci.yml/badge.svg)](https://github.com/Ruby-Sploit-King/pulsedeck/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.11%2B-7aa2f7?logo=python&logoColor=white)](https://www.python.org/)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-9ece6a)](LICENSE)

</div>

![PulseDeck dashboard](docs/pulsedeck-screenshot.png)

## Features

- Rich, Tokyo Night themed terminal dashboard with a gradient ASCII logo,
  GitHub-style badges, and colored status tables.
- Register any number of services under short, unique names.
- Validate names and require absolute HTTP(S) URLs (no embedded credentials).
- Probe services with a configurable timeout and measure real latency.
- `UP` / `DOWN` status derived from HTTP 2xx–3xx responses.
- Persistent history in SQLite at `~/.local/share/pulsedeck/pulsedeck.db`.
- Per-service check history and full JSON export.
- Export reports to disk for automation or archival.
- Safe by design: removing a service never touches the monitored endpoint.
- Tested with pytest, Ruff, mypy, and GitHub Actions CI.

## One-line install

Paste this into your terminal to download and install PulseDeck:

```bash
curl -fsSL https://raw.githubusercontent.com/Ruby-Sploit-King/pulsedeck/main/install.sh | bash
```

The installer uses [pipx](https://pipx.pypa.io) or [uv](https://docs.astral.sh/uv/)
when available, and falls back to `pip install --user`. When it finishes, run:

```bash
pulsedeck
```

## Other install options

With [pipx](https://pipx.pypa.io):

```bash
pipx install git+https://github.com/Ruby-Sploit-King/pulsedeck.git
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv tool install git+https://github.com/Ruby-Sploit-King/pulsedeck.git
```

From a local clone (development):

```bash
git clone https://github.com/Ruby-Sploit-King/pulsedeck.git
cd pulsedeck
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Requirements

- Python 3.11 or newer.
- Network access to the services you register.

## Usage

Run `pulsedeck` with no arguments to open the dashboard, then manage services
with the commands below.

```bash
pulsedeck                                  # open the dashboard
pulsedeck add api https://example.com/health
pulsedeck list                             # show all services and status
pulsedeck check                            # check every service
pulsedeck check api --timeout 2            # check one service
pulsedeck history api --limit 10           # recent checks for a service
pulsedeck export reports/pulsedeck.json    # write a JSON report
pulsedeck remove api                        # remove a service and its history
```

### Commands

| Command   | Description                                            |
| --------- | ------------------------------------------------------ |
| `add`     | Register a service for monitoring.                     |
| `list`    | Display all registered services and their status.      |
| `check`   | Check one service, or all of them when no name is given.|
| `history` | Show recent health checks for a service.               |
| `remove`  | Remove a service and its check history.                |
| `export`  | Export services and history as JSON.                   |

### Example session

```text
$ pulsedeck add api https://example.com
◆ Registered api.

$ pulsedeck check api
UP api  152.9 ms  HTTP 200 · HTTP response received
```

## Data and storage

PulseDeck keeps everything in a single SQLite database:

```text
~/.local/share/pulsedeck/pulsedeck.db
```

- `services` holds the current state and last result for each name.
- `checks` holds an append-only history used by `pulsedeck history`.
- Deleting a service removes its history but never the remote service.

## Docker

```bash
docker build -t pulsedeck .
docker run --rm -v pulsedeck-data:/root/.local/share/pulsedeck pulsedeck list
```

## Project layout

```text
pulsedeck/
├── main.py                  # Typer CLI and command definitions
├── pulsedeck/
│   ├── models.py            # Service and CheckResult dataclasses
│   ├── probes.py            # validation and HTTP health checks
│   ├── registry.py          # SQLite persistence and JSON export
│   └── terminal_ui.py       # Tokyo Night theme, banner, tables
├── tests/                   # pytest suite
├── install.sh               # one-line installer
└── docs/                    # screenshots
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"

ruff check .                 # lint
mypy .                       # type-check
pytest                       # run the test suite
```

## License

Released under the [MIT License](LICENSE).

---

Built by [Ruby-Sploit-King](https://github.com/Ruby-Sploit-King).
