# Event‑Processing Center Module Design

## 1. Purpose

Provide a modular, easily extensible center module (\`EventProcessor\`) that routes and processes various runtime events, orchestrates downstream actions (load testing, throughput recording, frequency adjustment), and returns the system to a stable state.

---

## 2. High‑Level Architecture

```
┌─────────────┐   Event   ┌────────────────────────┐
│EventDetector│──────────▶│   EventProcessor       │
└─────────────┘           │ • route event→handler  │
                          │ • manage state machine │
                          │ • inject shared ctx    │
                          └────────┬──────┬────────┘
                                   │      │
         ┌─────────────────────────┘      └─────────────────────────┐
         ▼                                                    ▼
  PressureTester                                   AdjustmentCoordinator
         │                                                    │
         ▼                                                    ▼
ThroughputRecorder  ◀──────────────────────────────────────── Dispatcher
```

---

## 3. Module Responsibilities

| Module                    | Single Responsibility                                              | Notes                         |
| ------------------------- | ------------------------------------------------------------------ | ----------------------------- |
| **EventDetector**         | Monitor metrics / hooks and emit `Event` objects.                  | Replaceable data sources.     |
| **EventProcessor**        | Central router + orchestrator. Maintains FSM (Stable / Adjusting). | Plug‑in handler map.          |
| **PressureTester**        | Run load tests to measure current max throughput.                  | Isolated, mockable.           |
| **ThroughputRecorder**    | Persist & query max throughput per deployment signature.           | Could be DB / Redis.          |
| **AdjustmentCoordinator** | Compute new request frequencies from target throughput.            | Strategy pattern.             |
| **Repository**            | In‑memory + persistent cache for configs, lookup tables.           | Shared dependency.            |
| **Dispatcher**            | Send control commands (HTTP/gRPC) to external Agents.              | Keeps network layer separate. |

---

## 4. EventProcessor Internal Components

* **EventRouter** — maps `event.type` → `Handler` class.
* **StateManager** — simple FSM guarding mutual exclusivity (e.g., prevents concurrent load tests).
* **Context** — DI container holding common services (repository, tester, etc.) for easy mocking.
* **Handler Plug‑ins** — one per event type, implement `handle(event, ctx)`.

### Example Built‑in Handlers

| Handler                       | Triggers                      | Workflow                                                                             |
| ----------------------------- | ----------------------------- | ------------------------------------------------------------------------------------ |
| `DeploymentChangeHandler`     | Deployment hash change        | 1. Check recorder → 2. Load test if needed → 3. Adjust frequency → 4. Back to stable |
| `HighLatencyHandler` (future) | Latency spike                 | Directly decrease frequency, flag for later retest                                   |
| `IdleSystemHandler` (future)  | Zero ratio high & queue empty | Reduce frequency or pause                                                            |

---

## 5. Key Interfaces (Python‑style pseudocode)

```python
@dataclass
class Event:
    type: str            # e.g. "DEPLOYMENT_CHANGE"
    payload: dict        # arbitrary data
    timestamp: datetime
    source: str          # detector name

class BaseHandler(ABC):
    @abstractmethod
    async def handle(self, event: Event, ctx: "Context") -> None:
        ...

class Context(NamedTuple):
    repo: Repository
    tester: PressureTester
    recorder: ThroughputRecorder
    adjuster: AdjustmentCoordinator
    dispatcher: Dispatcher
    state: StateManager
```

---

## 6. Example Sequence: Deployment Change

1. Detector emits `DEPLOYMENT_CHANGE` (payload contains new image hash).
2. **EventProcessor** routes to `DeploymentChangeHandler`.
3. Handler queries **ThroughputRecorder**.
4. If missing record → invoke **PressureTester**; else skip step 4.
5. Save max throughput to recorder.
6. Call **AdjustmentCoordinator** to compute new frequency.
7. Use **Dispatcher** to inform Agents.
8. **StateManager** flips back to Stable.

---

## 7. Extensibility Guidelines

* New Event = new Handler class + `processor.register_handler()`; core stays untouched.
* Adjustment strategies live behind an interface so PID, RL, or heuristic approaches can be hot‑swapped.
* Detector & Dispatcher abstract network/IO; unit tests can use pure‑in‑mem stubs.

---

## 8. Implementation Roadmap

1. **Define data classes & base interfaces** (`Event`, `BaseHandler`, `Context`).
2. Minimal **EventProcessor** skeleton with registry & state machine.
3. Stub services (PressureTester, Recorder, etc.) and wire `DeploymentChangeHandler` only.
4. Integrate real implementations & persistence (e.g., Postgres or Redis for recorder).
5. Add metrics + logging, write unit & integration tests.
6. Gradually plug in other events and strategies.

---

## 9. Testing Strategy

* **Unit tests** for each Handler using mock services.
* **Integration tests** for Processor routing and state transitions.
* **Load tests** against PressureTester separately.
* **End‑to‑end**: simulate detectors via fake events, assert Agent receives correct commands.

---

## 10. Future Work

* Async task queue or Actor system for higher throughput of event handling.
* Distributed EventProcessor cluster with sticky‑session sharding.
* Dynamic config reload for handler registry (YAML‑driven).
* UI dashboard summarizing events, actions, and current state.
