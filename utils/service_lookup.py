from typing import Any, Dict, List, Optional


def get_agents_for_service(data: Dict[str, Any], service_id: str) -> List[str]:
    """Return all agent IDs providing the given service."""
    agents: List[str] = []
    for node in data.get("nodes", []):
        for service in node.get("services", []):
            if service.get("id") == service_id:
                agents.extend(service.get("agents", []))
    return agents


def get_service_node(data: Dict[str, Any], service_id: str) -> Optional[str]:
    """Return the node ID hosting ``service_id`` if present."""
    for node in data.get("nodes", []):
        for service in node.get("services", []):
            if service.get("id") == service_id:
                return node.get("id")
    return None


def get_services_on_node(data: Dict[str, Any], node_id: str) -> List[str]:
    """Return a list of services available on ``node_id``."""
    for node in data.get("nodes", []):
        if node.get("id") == node_id:
            return [svc.get("id") for svc in node.get("services", [])]
    return []
