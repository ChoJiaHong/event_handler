import asyncio
from typing import List, Dict
from .agent_load_simulator import AgentLoadSimulator

class FrequencyTestExecutor:
    """頻率測試執行器"""
    
    def __init__(self, simulator: AgentLoadSimulator = None):
        self.simulator = simulator or AgentLoadSimulator()
    
    async def test_frequency(self, agents: List[Dict], frequency: int, deployment_hash: str) -> bool:
        """測試指定頻率"""
        try:
            interval = 1.0 / frequency if frequency > 0 else 1.0
            test_duration = 10
            
            tasks = [
                asyncio.create_task(
                    self.simulator.simulate_load(agent, interval, test_duration, deployment_hash)
                ) for agent in agents
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for result in results if result is True)
            success_rate = success_count / len(agents)
            
            return success_rate >= 0.8
            
        except Exception as e:
            print(f"頻率測試失敗: {e}")
            return False