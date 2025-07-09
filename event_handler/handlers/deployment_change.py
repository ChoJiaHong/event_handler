from ..event import Event
from ..context import Context
from .base import BaseHandler

class DeploymentChangeHandler(BaseHandler):
    async def handle(self, event: Event, ctx: Context) -> None:
        deployment_hash = event.payload.get("hash")
        if deployment_hash is None:
            return
        throughput = await ctx.recorder.get(deployment_hash)
        if throughput is None:
            throughput = await ctx.tester.load_test(deployment_hash)
            await ctx.recorder.save(deployment_hash, throughput)
        frequency = await ctx.adjuster.compute_frequency(throughput)
        await ctx.dispatcher.dispatch(frequency)
