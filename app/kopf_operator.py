"""Kopf-based operator that feeds Kubernetes events into the domain event processor."""

from datetime import datetime
from typing import Any

import kopf

from app.main import build_context, create_bus
from shared import Event
from features.deployment_change.domain import deployment_change_detector


class KopfEventBridge:
    """Bridge translating Kopf callbacks into domain events.

    The bridge keeps the event processing logic isolated from Kopf so the
    infrastructure layer can be replaced or extended without touching the
    domain code.  This maintains high cohesion and low coupling in line with
    DDD principles.
    """

    def __init__(self) -> None:
        self._bus = create_bus(build_context())

    async def forward(self, spec: dict[str, Any]) -> None:
        event = Event(
            type=spec.get("type"),
            payload=spec.get("payload", {}),
            timestamp=datetime.utcnow(),
            source="kopf",
        )
        print(f"Forwarding event: {event}")
        await self._bus.publish(event)


_bridge = KopfEventBridge()


@kopf.on.update("ha.example.com", "v1", "services")
async def handle_kopf_event(spec, **_: Any) -> None:
    """Receive custom resources and forward them to the event processor."""
    _bridge.forward(spec)
    print(f"Service CR updated, new spec: {spec}")



GROUP = "ha.example.com"
VERSION = "v1"
PLURAL = "services"

    
@kopf.on.field("ha.example.com", "v1", "services", field="spec")
async def service_deploy_changed(body: dict, meta: dict, old: Any, new: Any, **_: Any):
    print(f"[EVENT] spec changed for {meta.get('namespace')}/{meta.get('name')}")
    print(f"[OLD] {old}")
    print(f"[NEW] {new}")

    changed, details = deployment_change_detector.has_deployment_changed(old, new)
    if changed:
        print("⚠ 部署環境發生變動！")
        print(f"變動詳情: {details['diff']}")
        
        # 創建符合 DeploymentChangeHandler 預期的事件格式
        deployment_event = {
            "type": "DEPLOYMENT_CHANGE",
            "payload": {
                "hash": {
                    "node": list(details['new_signatures'].keys())[0] if details['new_signatures'] else "unknown",
                    "services": _extract_service_counts(new)
                },
                #"old_spec": old,
                "new_spec": new,
                #"diff": details['diff'],
                #"namespace": meta.get('namespace'),
                #"name": meta.get('name')
            }
        }

        print(f"\nForwarding deployment change event: {deployment_event}\n")
        await _bridge.forward(deployment_event)
        print(f"Deployment change event forwarded")
    else:
        print("✅ 部署環境無變動")
        
        
def _extract_service_counts(spec):
    """從 spec 中提取服務計數"""
    counts = {}
    for item in spec.get("raw", []):
        service_type = item.get("serviceType")
        if service_type:
            counts[service_type] = counts.get(service_type, 0) + 1
    return counts



#print(f"\nForwarding deployment change event: {deployment_event}\n")
""" {
  "type": "DEPLOYMENT_CHANGE",
  "payload": {
    "hash": {
      "node": "workergpu",
      "services": {
        "gesture": 3
      }
    },
    "old_spec": {
      "raw": [
        {
          "currentConnection": 4,
          "currentFrequency": 30,
          "frequencyLimit": [30, 15],
          "hostIP": "10.52.52.25",
          "hostPort": 30501,
          "nodeName": "workergpu",
          "podIP": "10.244.1.72",
          "serviceType": "gesture",
          "workloadLimit": 90.5
        },
        {
          "currentConnection": 4,
          "currentFrequency": 30,
          "frequencyLimit": [30, 15],
          "hostIP": "10.52.52.25",
          "hostPort": 30501,
          "nodeName": "workergpu",
          "podIP": "10.244.1.72",
          "serviceType": "gesture",
          "workloadLimit": 90.5
        }
      ]
    },
    "new_spec": {
      "raw": [
        {
          "currentConnection": 4,
          "currentFrequency": 30,
          "frequencyLimit": [30, 15],
          "hostIP": "10.52.52.25",
          "hostPort": 30501,
          "nodeName": "workergpu",
          "podIP": "10.244.1.72",
          "serviceType": "gesture",
          "workloadLimit": 90.5
        },
        {
          "currentConnection": 4,
          "currentFrequency": 30,
          "frequencyLimit": [30, 15],
          "hostIP": "10.52.52.25",
          "hostPort": 30501,
          "nodeName": "workergpu",
          "podIP": "10.244.1.72",
          "serviceType": "gesture",
          "workloadLimit": 90.5
        },
        {
          "currentConnection": 4,
          "currentFrequency": 30,
          "frequencyLimit": [30, 15],
          "hostIP": "10.52.52.25",
          "hostPort": 30501,
          "nodeName": "workergpu",
          "podIP": "10.244.1.72",
          "serviceType": "gesture",
          "workloadLimit": 90.5
        }
      ]
    },
    "diff": {
      "added_nodes": [],
      "removed_nodes": [],
      "changed_nodes": {
        "workergpu": {
          "added": {
            "gesture": 1
          },
          "removed": {},
          "delta": {
            "gesture": 1
          }
        }
      }
    },
    "namespace": "arha-system",
    "name": "service-info"
  }
} """
