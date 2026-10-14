from dataclasses import asdict, dataclass
from datetime import UTC, datetime


@dataclass(frozen=True)
class Service:
    name: str 
    url: str 
    last_status: str 
    last_checked_at: str | None  
    last_latency_ms: float | None 
    last_message: str 

@dataclass(frozen=True)
class CheckResult:
    name: str 
    url: str 
    status: str 
    status_code: int | None 
    latency_ms: float 
    message: str 
    checked_at: str 

    @classmethod 
    def create(
        cls,
        name: str,
        url: str,
        status: str,
        status_code: int | None,
        latency_ms: float,
        message: str,
    ) -> "CheckResult":
        return cls(
            name=name,
            url=url,
            status=status,
            status_code=status_code,
            latency_ms=round(latency_ms, 2),
            message=message,
            checked_at=datetime.now(UTC).isoformat(),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)