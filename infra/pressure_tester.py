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
        """執行負載測試"""
        # 獲取 agents
        subscription_data = await self.k8s_client.get_subscription_info()
        if not subscription_data:
            return 0
            
        agents = subscription_data.get('raw', [])
        if not agents:
            return 0
        
        # 執行測試
        return await self._execute_load_test(agents, deployment_hash)
    
    async def _execute_load_test(self, agents: List[Dict], deployment_hash: str) -> int:
        """執行測試流程"""
        current_frequency = self.config.initial_frequency
        max_successful_frequency = 0
        
        print(f"開始對 {len(agents)} 個 agents 進行壓力測試...")
        
        while current_frequency <= self.config.max_frequency:
            print(f"測試頻率: {current_frequency} 請求/秒")
            
            success = await self.test_executor.test_frequency(
                agents, current_frequency, deployment_hash
            )
            
            if success:
                max_successful_frequency = current_frequency
                print(f"✓ 頻率 {current_frequency} 測試成功")
                current_frequency += self.config.frequency_step
            else:
                print(f"✗ 頻率 {current_frequency} 測試失敗，停止測試")
                break
                
            await asyncio.sleep(self.config.recovery_time)
        
        print(f"壓力測試完成，最大成功頻率: {max_successful_frequency} 請求/秒")
        return max_successful_frequency
