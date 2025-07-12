from utils.service_lookup import (
    get_agents_for_service,
    get_service_node,
    get_services_on_node,
)

sample_data = {
    "nodes": [
        {
            "id": "edge01",
            "services": [
                {"id": "pose", "agents": ["agentA", "agentB"]},
                {"id": "gesture", "agents": ["agentA"]},
            ],
        },
        {
            "id": "edge02",
            "services": [
                {"id": "object", "agents": ["agentC"]},
                {"id": "pose", "agents": ["agentC"]},
            ],
        },
    ]
}


def test_get_agents_for_service():
    agents = get_agents_for_service(sample_data, "pose")
    assert set(agents) == {"agentA", "agentB", "agentC"}


def test_get_service_node():
    assert get_service_node(sample_data, "object") == "edge02"
    assert get_service_node(sample_data, "gesture") == "edge01"


def test_get_services_on_node():
    assert set(get_services_on_node(sample_data, "edge01")) == {"pose", "gesture"}
    assert set(get_services_on_node(sample_data, "edge02")) == {"object", "pose"}
