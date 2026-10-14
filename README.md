# PulseDeck

PulseDeck is a neon-styled terminal dashboard for HTTP service health.
Register services under short names, probe them over HTTP(S), track status
and latency history in a persistent SQLite registry, and export the deck to
JSON.

![PulseDeck example](docs/pulsedeck-screenshot.png)

## Features

- Rich terminal dashboard with a gradient logo, badges, and status tables.
- Unique service names with validated absolute HTTP(S) URLs.
- Health checks with configurable timeouts and measured latency.
- UP/DOWN status from HTTP 2xx-3xx responses.
- SQLite persistence at `~/.local/share/pulsedeck/pulsedeck.db`.
- Per-service check history and JSON export.
- pytest tests, Ruff, mypy, and GitHub Actions CI.
- Removing a service never deletes or changes the monitored service itself.

## Requirements

Python 3.11+ and network access for health checks.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Usage

```bash
pulsedeck add api https://example.com/health
pulsedeck list
pulsedeck check
pulsedeck check api --timeout 2
pulsedeck history api --limit 10
pulsedeck export reports/pulsedeck.json
pulsedeck remove api
```

Run `pulsedeck` with no arguments to open the dashboard.

## Docker

```bash
docker build -t pulsedeck .
docker run --rm -v pulsedeck-data:/root/.local/share/pulsedeck pulsedeck list
```
