from typing import NamedTuple

from core.services import (
    Repository,
    PressureTester,
    ThroughputRepository,
    AdjustmentStrategy,
    Dispatcher,
)
from core.domain import StateManager

class Context(NamedTuple):
    repo: Repository
    tester: PressureTester
    recorder: ThroughputRepository
    adjuster: AdjustmentStrategy
    dispatcher: Dispatcher
    state: StateManager
