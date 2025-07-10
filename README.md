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

## Running tests

```
pytest -q
```
