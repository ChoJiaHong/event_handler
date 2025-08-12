from dataclasses import dataclass

@dataclass
class LoadTestConfig:
    """負載測試配置"""
    initial_frequency: int = 1
    max_frequency: int = 1000
    frequency_step: int = 10
    success_threshold: float = 0.8
    agent_success_threshold: float = 0.9
    recovery_time: int = 2