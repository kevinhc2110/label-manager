from pydantic import BaseModel


class PrinterResponse(BaseModel):
    id: str
    name: str
    ip_address: str
    port: int
    location: str
    is_active: bool


class PrintLabelResponse(BaseModel):
    message: str
    printer_id: str
