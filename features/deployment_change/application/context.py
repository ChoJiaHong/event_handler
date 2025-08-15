from typing import NamedTuple

from ..domain.services import (
    Repository,
    PressureTester,
    ThroughputRepository,
    AdjustmentStrategy,
    Dispatcher,
)
from shared import StateManager


class Context(NamedTuple):
    repo: Repository
    tester: PressureTester
    recorder: ThroughputRepository
    adjuster: AdjustmentStrategy
    dispatcher: Dispatcher
    state: StateManager
