import json
import sqlite3
from pathlib import Path

from pulsedeck.models import CheckResult, Service


def default_database() -> Path:
    return Path.home() / ".local" / "share" / "pulsedeck" / "pulsedeck.db"


class Registry:
    def __init__(self, database: Path | None = None) -> None:
        self.database = database or default_database()
        self.database.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS services (
                    name TEXT PRIMARY KEY,
                    url TEXT NOT NULL,
                    last_status TEXT NOT NULL DEFAULT 'UNKNOWN',
                    last_checked_at TEXT,
                    last_latency_ms REAL,
                    last_message TEXT NOT NULL DEFAULT 'Not checked yet'
                );

                CREATE TABLE IF NOT EXISTS checks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    service_name TEXT NOT NULL,
                    url TEXT NOT NULL,
                    status TEXT NOT NULL,
                    status_code INTEGER,
                    latency_ms REAL NOT NULL,
                    message TEXT NOT NULL,
                    checked_at TEXT NOT NULL,
                    FOREIGN KEY(service_name)
                        REFERENCES services(name)
                        ON DELETE CASCADE
                );

                CREATE INDEX IF NOT EXISTS idx_checks_service_time
                ON checks(service_name, checked_at DESC);
                """
            )

    def add(self, name: str, url: str) -> None:
        with self._connect() as connection:
            connection.execute(
                "INSERT INTO services (name, url) VALUES (?, ?)",
                (name, url),
            )

    def list_services(self) -> list[Service]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM services ORDER BY name"
            ).fetchall()

        return [Service(**dict(row)) for row in rows]

    def get(self, name: str) -> Service | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM services WHERE name = ?",
                (name,),
            ).fetchone()

        return Service(**dict(row)) if row else None

    def record(self, result: CheckResult) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO checks (
                    service_name, url, status, status_code,
                    latency_ms, message, checked_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.name,
                    result.url,
                    result.status,
                    result.status_code,
                    result.latency_ms,
                    result.message,
                    result.checked_at,
                ),
            )
            connection.execute(
                """
                UPDATE services
                SET last_status = ?,
                    last_checked_at = ?,
                    last_latency_ms = ?,
                    last_message = ?
                WHERE name = ?
                """,
                (
                    result.status,
                    result.checked_at,
                    result.latency_ms,
                    result.message,
                    result.name,
                ),
            )

    def history(self, name: str, limit: int = 20) -> list[dict[str, object]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT status, status_code, latency_ms, message, checked_at
                FROM checks
                WHERE service_name = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (name, limit),
            ).fetchall()

        return [dict(row) for row in rows]

    def remove(self, name: str) -> bool:
        with self._connect() as connection:
            cursor = connection.execute(
                "DELETE FROM services WHERE name = ?",
                (name,),
            )

        return cursor.rowcount > 0

    def export_data(self) -> dict[str, object]:
        with self._connect() as connection:
            services = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM services ORDER BY name"
                )
            ]
            checks = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM checks ORDER BY id"
                )
            ]

        return {"services": services, "checks": checks}

    def export_json(self, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            json.dumps(self.export_data(), indent=2),
            encoding="utf-8",
        )