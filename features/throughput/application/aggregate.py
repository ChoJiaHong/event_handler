from event_bus import subscribe
from shared.logger import get_logger
from shared.event import Event
from .context import Context
from .handlers.deployment_change import DeploymentChangeHandler
from .handlers.high_latency import HighLatencyHandler
from .handlers.idle_system import IdleSystemHandler

logger = get_logger(__name__)


def _wrap(handler, ctx: Context):
    async def _inner(event: Event):
        entered = await ctx.state.try_enter_adjusting()
        if not entered:
            return
        try:
            await handler.handle(event, ctx)
        finally:
            await ctx.state.exit_adjusting()
    return _inner


def register(ctx: Context) -> None:
    """Register throughput handlers on the global event bus."""
    subscribe("DEPLOYMENT_CHANGE", _wrap(DeploymentChangeHandler(), ctx))
    subscribe("HIGH_LATENCY", _wrap(HighLatencyHandler(), ctx))
    subscribe("IDLE_SYSTEM", _wrap(IdleSystemHandler(), ctx))
    logger.info("Throughput handlers registered")

__all__ = ["register", "Context"]
