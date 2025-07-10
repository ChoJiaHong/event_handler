from typing import NamedTuple

from .services.repository import Repository
from .services.pressure_tester import PressureTester
from .services.throughput_recorder import ThroughputRecorder
from .services.adjustment_coordinator import AdjustmentCoordinator
from .services.dispatcher import Dispatcher
from .services.state_manager import StateManager
from .services.prometheus import PrometheusService

class Context(NamedTuple):
    repo: Repository
    tester: PressureTester
    recorder: ThroughputRecorder
    adjuster: AdjustmentCoordinator
    dispatcher: Dispatcher
    state: StateManager
    prometheus: PrometheusService
