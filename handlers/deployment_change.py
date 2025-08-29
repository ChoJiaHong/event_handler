import logging

from core.domain import Event
from core.context import Context
from .base import BaseHandler

logger = logging.getLogger(__name__)

class DeploymentChangeHandler(BaseHandler):
    async def handle(self, event: Event, ctx: Context) -> None:
        deployment_hash = event.payload.get("hash")
        logger.info("Deployment change event received: %s", deployment_hash)
        
        if deployment_hash is None:
            logger.info("No deployment hash provided")
            return
        
        # 檢查是否有現有的吞吐量記錄
        throughput = await ctx.recorder.get(deployment_hash)
        logger.info("Throughput lookup result: %s", throughput)
        
        if throughput is None:
            logger.info("Running multi-service load test for %s", deployment_hash)
            
            # 執行多服務壓力測試
            throughput = await ctx.tester.load_test(deployment_hash)
            
            # 獲取詳細的服務吞吐量資訊
            service_throughputs = await ctx.tester.get_last_service_throughputs()
            
            # 儲存詳細的服務吞吐量（包含總和）
            if service_throughputs:
                await ctx.recorder.save_service_throughputs(deployment_hash, service_throughputs)
                logger.info("Recorded service throughputs: %s", service_throughputs)
                logger.info("Recorded total throughput: %s", throughput)
            else:
                # 如果沒有詳細資料，就只儲存總吞吐量
                await ctx.recorder.save(deployment_hash, throughput)
                logger.info("Recorded total throughput %s", throughput)
            
            # 移除已註解的程式碼，因為我們已經在上面實現了
        
        # 計算新頻率並分發
        frequency = await ctx.adjuster.compute_frequency(throughput)
        await ctx.dispatcher.dispatch(frequency)
        logger.info("Dispatched frequency %s", frequency)
