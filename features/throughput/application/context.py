from typing import NamedTuple

from features.throughput.domain.aggregate import (
    Repository,
    PressureTester,
    ThroughputRepository,
    AdjustmentStrategy,
    Dispatcher,
    StateManager,
)

class Context(NamedTuple):
    repo: Repository
    tester: PressureTester
    recorder: ThroughputRepository
    adjuster: AdjustmentStrategy
    dispatcher: Dispatcher
    state: StateManager
