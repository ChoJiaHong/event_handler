from dataclasses import dataclass
from typing import Dict

@dataclass
class ThroughputKey:
    """Structured identifier for throughput entries."""

    node_name: str
    service_counts: Dict[str, int]

    def to_string(self) -> str:
        sorted_services = sorted(
            (svc, cnt) for svc, cnt in self.service_counts.items() if cnt > 0
        )
        if not sorted_services:
            return self.node_name
        parts = [f"{svc}={cnt}" for svc, cnt in sorted_services]
        return f"{self.node_name}:{','.join(parts)}"
