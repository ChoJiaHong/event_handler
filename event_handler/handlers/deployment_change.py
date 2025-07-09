import logging

from ..event import Event
from ..context import Context
from .base import BaseHandler

logger = logging.getLogger(__name__)

class DeploymentChangeHandler(BaseHandler):
    async def handle(self, event: Event, ctx: Context) -> None:
        deployment_hash = event.payload.get("hash")
        logger.info("Deployment change event received: %s", deployment_hash)
        if deployment_hash is None:
            logger.info("No deployment hash provided")
            return
        throughput = await ctx.recorder.get(deployment_hash)
        logger.info("Throughput lookup result: %s", throughput)
        if throughput is None:
            logger.info("Running load test for %s", deployment_hash)
            throughput = await ctx.tester.load_test(deployment_hash)
            await ctx.recorder.save(deployment_hash, throughput)
            logger.info("Recorded throughput %s", throughput)
        frequency = await ctx.adjuster.compute_frequency(throughput)
        await ctx.dispatcher.dispatch(frequency)
        logger.info("Dispatched frequency %s", frequency)
