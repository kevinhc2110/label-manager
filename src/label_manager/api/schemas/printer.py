from datetime import datetime

from pydantic import BaseModel


class PrinterResponse(BaseModel):
    id: str
    name: str
    ip_address: str
    port: int
    location: str
    is_active: bool


class PrintLabelRequest(BaseModel):
    text: str = "Hola Mundo"
    qr_data: str | None = None
    copies: int = 1


class PrintLabelResponse(BaseModel):
    message: str
    printer_id: str


class PrinterHealthResponse(BaseModel):
    printer_id: str
    name: str
    ip_address: str
    port: int
    is_online: bool
    latency_ms: float | None = None


class WebhookPrintRequest(BaseModel):
    printer_id: str
    text: str | None = None
    qr_data: str | None = None
    copies: int = 1
    template_name: str | None = None
    variables: dict | None = None


class BatchPrintItem(BaseModel):
    printer_id: str
    text: str | None = None
    qr_data: str | None = None
    copies: int = 1
    variables: dict | None = None


class BatchPrintRequest(BaseModel):
    jobs: list[BatchPrintItem]


class PrintJobResponse(BaseModel):
    id: str
    printer_id: str
    text: str | None
    qr_data: str | None
    copies: int
    status: str
    retry_count: int
    error: str | None
    created_at: datetime | None
    processed_at: datetime | None


class LabelTemplateResponse(BaseModel):
    id: str
    name: str
    content_template: str
    created_at: datetime | None


class LabelTemplateCreate(BaseModel):
    name: str
    content_template: str
