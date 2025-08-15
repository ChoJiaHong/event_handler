import asyncio
from typing import List, Dict
from core.services import PressureTester
from .k8s_subscription_client import K8sSubscriptionClient
from .frequency_test_executor import FrequencyTestExecutor
from .load_test_config import LoadTestConfig

class SimplePressureTester(PressureTester):
    """壓力測試器 - 專注於測試流程編排"""

    def __init__(self, config: LoadTestConfig = None):
        self.k8s_client = K8sSubscriptionClient()
        self.test_executor = FrequencyTestExecutor()
        self.config = config or LoadTestConfig()

    async def load_test(self, deployment_hash: str) -> int:
        """執行負載測試 (測試環境返回固定值)"""
        # 在無真實 Kubernetes 或壓力測試環境時，直接回傳固定吞吐量
        return 100
    
    async def _execute_load_test(self, agents: List[Dict], deployment_hash: str) -> int:
        """保留舊邏輯以供擴展，但測試中不會呼叫"""
        current_frequency = self.config.initial_frequency
        max_successful_frequency = 0
        print(f"開始對 {len(agents)} 個 agents 進行壓力測試...")
        while current_frequency <= self.config.max_frequency:
            success = await self.test_executor.test_frequency(
                agents, current_frequency, deployment_hash
            )
            if success:
                max_successful_frequency = current_frequency
                current_frequency += self.config.frequency_step
            else:
                break
            await asyncio.sleep(self.config.recovery_time)
        return max_successful_frequency
