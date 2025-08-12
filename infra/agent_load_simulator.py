import asyncio
import random
from typing import Dict

class AgentLoadSimulator:
    """Agent 負載模擬器"""
    
    async def simulate_load(self, agent: Dict, interval: float, duration: int, deployment_hash: str) -> bool:
        """模擬單個 agent 的負載"""
        try:
            start_time = asyncio.get_event_loop().time()
            success_count = 0
            total_requests = 0
            
            while (asyncio.get_event_loop().time() - start_time) < duration:
                try:
                    await self._send_request(agent, deployment_hash)
                    success_count += 1
                except:
                    pass
                
                total_requests += 1
                await asyncio.sleep(interval)
            
            success_rate = success_count / total_requests if total_requests > 0 else 0
            return success_rate >= 0.9
            
        except Exception as e:
            print(f"Agent 模擬失敗: {e}")
            return False
    
    async def _send_request(self, agent: Dict, deployment_hash: str):
        """發送請求到 agent"""
        await asyncio.sleep(0.01)  # 模擬延遲
        if random.random() < 0.05:  # 5% 失敗率
            raise Exception("模擬請求失敗")