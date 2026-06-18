from dataclasses import dataclass
from datetime import datetime


@dataclass
class LabelTemplate:
    id: str
    name: str
    content_template: str
    created_at: datetime | None
