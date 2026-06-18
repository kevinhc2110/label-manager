from dataclasses import dataclass
from datetime import datetime


@dataclass
class PrintJob:
    id: str
    printer_id: str
    template_id: str | None
    text: str | None
    qr_data: str | None
    copies: int
    variables: dict | None
    status: str
    retry_count: int
    max_retries: int
    error: str | None
    created_at: datetime | None
    processed_at: datetime | None
