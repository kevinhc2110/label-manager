
from dataclasses import dataclass


@dataclass
class Printer:
    id: str
    name: str
    ip_address: str
    port: int
    location: str
    is_active: bool