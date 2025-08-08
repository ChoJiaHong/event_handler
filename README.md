# Event Handler

This repository provides a minimal implementation of an event processing center as described in the software requirements specification.
The `EventProcessor` routes incoming events to registered handlers while coordinating supporting services.  Only a `DeploymentChangeHandler` is included as an example.

## Throughput keys

`ThroughputRecorder` operations accept either the legacy string key format or a
dictionary with `node` and `services` fields.  Example:

```python
deployment = {"node": "node1", "services": {"pose": 1, "gesture": 2}}
await recorder.save(deployment, 100, "pose")
```
The dictionary is converted internally to the canonical key so lookups are
order independent.

## Kopf operator

[Kopf](https://kopf.readthedocs.io/) can be used to trigger domain events from
Kubernetes.  The operator defined in `infra/kopf_operator.py` listens for
custom resources of kind `Event` in group `example.com` and forwards them to
the domain `EventProcessor`.

Run the operator:

```bash
pip install kopf
kopf run infra/kopf_operator.py
```

Creating a custom resource with fields `spec.type` and `spec.payload` will
create a domain event with those values and process it with all registered
handlers.

### Extending

Handlers remain decoupled from the operator.  To add a new event type:

```python
from handlers.base import BaseHandler

class ScaleUpHandler(BaseHandler):
    async def handle(self, event, ctx):
        ...

processor.register_handler("SCALE_UP", ScaleUpHandler())
```

## Running tests

```
pytest -q
```
