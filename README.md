# Event Handler

This repository provides a minimal implementation of an event processing center as described in the software requirements specification.  
The `EventProcessor` routes incoming events to registered handlers while coordinating supporting services.  Only a `DeploymentChangeHandler` is included as an example.

## Running tests

```
pytest -q
```
