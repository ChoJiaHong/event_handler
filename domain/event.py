from dataclasses import dataclass
from datetime import datetime

@dataclass
class Event:
    type: str
    payload: dict
    timestamp: datetime
    source: str
