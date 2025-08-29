import asyncio
from typing import List, Dict
from core.services import PressureTester
from .k8s_subscription_client import CrdRepository
from .frequency_test_executor import FrequencyTestExecutor
from .load_test_config import LoadTestConfig
import requests
import json
from infra.prometheus_client import PrometheusClient

class SimplePressureTester(PressureTester):
    """壓力測試器 - 專注於測試流程編排"""

    def __init__(self, config: LoadTestConfig = None):
        self.k8s_client = CrdRepository()
        self.test_executor = FrequencyTestExecutor()
        self.config = config or LoadTestConfig()

    async def load_test(self, deployment_hash: str) -> int:
        """
        執行負載測試，支援多服務同時測試
        
        Input:
        - deployment_hash: 部署雜湊值，包含節點和服務資訊
        
        Output:
        - int: 系統整體最大吞吐量
        
        Raises:
        - ValueError: 當部署資訊格式不正確時
        - RuntimeError: 當無法獲取訂閱資訊時
        - Exception: 其他測試執行錯誤
        """
        # 驗證輸入參數
        if not deployment_hash:
            raise ValueError("deployment_hash 不能為空")
        
        if not isinstance(deployment_hash, dict):
            raise ValueError(f"deployment_hash 必須是字典，實際類型: {type(deployment_hash)}")
        
        # 解析部署資訊
        node_name = deployment_hash.get("node")
        service_counts = deployment_hash.get("services")
        
        if not node_name:
            raise ValueError("deployment_hash 中缺少 'node' 欄位")
        
        if not service_counts or not isinstance(service_counts, dict):
            raise ValueError("deployment_hash 中缺少有效的 'services' 欄位")
        
        if not service_counts:
            raise ValueError("services 不能為空")
        
        print(f"開始對節點 {node_name} 的多服務進行壓力測試")
        print(f"服務分布: {service_counts}")
        
        # 獲取所有相關的 agents
        agents_list = await self.k8s_client.get_subscription_info()
        
        if not agents_list:
            raise RuntimeError("無法獲取訂閱資訊或訂閱資訊為空")
        
        if not isinstance(agents_list, list):
            raise RuntimeError(f"訂閱資訊格式錯誤，期望 list，實際: {type(agents_list)}")
        
        print(f"總共找到 {len(agents_list)} 個 agents")
        print(f"agent_list 範例: {agents_list}")
        # 按服務類型分組 agents
        service_agents = self._group_agents_by_service(
            agents_list,
            node_name, 
            service_counts
        )
        print(f"service_agents 範例: {service_agents}")
        if not service_agents:
            raise RuntimeError(f"在節點 {node_name} 上沒有找到符合條件的 agents")
        
        
        
        
        # 對每個服務進行並行壓力測試
        service_throughputs = await self._test_multiple_services(
            service_agents, deployment_hash
        )
        
        # 驗證測試結果
        failed_services = [service for service, throughput in service_throughputs.items() if throughput <= 0]
        if failed_services:
            raise RuntimeError(f"以下服務的壓力測試失敗: {failed_services}")
        
        # 計算整體吞吐量
        total_throughput = sum(service_throughputs.values())
        
        if total_throughput <= 0:
            raise RuntimeError("總吞吐量計算結果無效")
        
        print(f"✅ 多服務壓力測試完成")
        print(f"各服務吞吐量: {service_throughputs}")
        print(f"總吞吐量: {total_throughput}")
        
        # 儲存詳細的服務吞吐量資訊
        self._last_service_throughputs = service_throughputs
        
        return total_throughput

    async def get_last_service_throughputs(self) -> Dict[str, int]:
        """
        獲取最後一次測試的詳細服務吞吐量資訊
        
        Output:
        - {service_type: throughput}
        """
        return getattr(self, '_last_service_throughputs', {})

    def _group_agents_by_service(
        self, 
        agents: List[Dict], 
        target_node: str, 
        service_counts: Dict[str, int]
    ) -> Dict[str, List[Dict]]:
        """
        根據服務類型和節點分組 agents（不限制數量）

        Input:
        - agents: 所有 agents 列表
        - target_node: 目標節點名稱
        - service_counts: 需要的服務類型 {"gesture": 2, "pose": 1}

        Output:
        - {service_type: [agents_list]}
        """
        if not isinstance(agents, list):
            raise ValueError(f"agents 必須是 list，實際類型: {type(agents)}")
        
        if not target_node:
            raise ValueError("target_node 不能為空")
        
        if not isinstance(service_counts, dict):
            raise ValueError(f"service_counts 必須是字典，實際類型: {type(service_counts)}")
        
        service_agents = {}
        
        for service_type in service_counts.keys():
            matching_agents = []
            for agent in agents:
                if not isinstance(agent, dict):
                    print(f"⚠️  跳過無效的 agent 資料: {agent}")
                    continue
                if (agent.get("serviceType") == service_type and 
                    agent.get("nodeName") == target_node):
                    matching_agents.append(agent)
            service_agents[service_type] = matching_agents
            print(f"服務 {service_type}: 找到 {len(matching_agents)} 個 agents")
        
        return service_agents
        

    async def _test_multiple_services(
        self, 
        service_agents: Dict[str, List[Dict]], 
        deployment_hash: str
    ) -> Dict[str, int]:
        """
        並行測試多個服務的吞吐量
        
        Input:
        - service_agents: {service_type: [agents]}
        - deployment_hash: 部署雜湊值
        
        Output:
        - {service_type: throughput}
        
        Raises:
        - RuntimeError: 當測試執行失敗時
        """
        if not service_agents:
            raise ValueError("service_agents 不能為空")
        
        tasks = []
        service_names = []
        
        node_name = deployment_hash.get("node")
        for service_type, agents in service_agents.items():
            if agents:  # 只有當有 agents 時才測試
                task = asyncio.create_task(
                    self._test_single_service(service_type, agents, node_name)
                )
                tasks.append(task)
                service_names.append(service_type)
        
        if not tasks:
            raise RuntimeError("沒有可執行的測試任務")
        
        # 並行執行所有服務的壓力測試
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 組合結果
        service_throughputs = {}
        errors = []
        
        for i, (service_name, result) in enumerate(zip(service_names, results)):
            if isinstance(result, Exception):
                error_msg = f"服務 {service_name} 測試失敗: {result}"
                print(f"❌ {error_msg}")
                errors.append(error_msg)
                service_throughputs[service_name] = 0
            else:
                if not isinstance(result, int) or result < 0:
                    error_msg = f"服務 {service_name} 返回無效的吞吐量: {result}"
                    print(f"❌ {error_msg}")
                    errors.append(error_msg)
                    service_throughputs[service_name] = 0
                else:
                    service_throughputs[service_name] = result
                    print(f"✅ 服務 {service_name} 最大吞吐量: {result}")
        
        if errors:
            raise RuntimeError(f"部分服務測試失敗: {'; '.join(errors)}")
        
        return service_throughputs

    async def _test_single_service(
        self, 
        service_type: str, 
        agents: List[Dict], 
        node_name: str
    ) -> int:
        """
        測試單一服務的最大吞吐量
        
        Input:
        - service_type: 服務類型
        - agents: 該服務的 agents 列表
        - node_name: 節點名稱

        Output:
        - int: 該服務的最大吞吐量
        
        Raises:
        - ValueError: 當輸入參數無效時
        - RuntimeError: 當測試執行失敗時
        """
        if not service_type:
            raise ValueError("service_type 不能為空")
        
        if not agents or not isinstance(agents, list):
            raise ValueError(f"agents 必須是非空 list，實際: {agents}")
        
        
        
        print(f"🔍 開始測試服務 {service_type} (共 {len(agents)} 個 agents)")

        # 初始化 Prometheus 客戶端
        prometheus_client = PrometheusClient()
        
        # 獲取初始的 CPS 和 RPS
        try:
            cps = await prometheus_client.get_cps_by_service_and_node(service_type, node_name)
            rps = await prometheus_client.get_rps_by_service_and_node(service_type, node_name)
            print(f"初始 CPS: {cps}, RPS: {rps}")
        except Exception as e:
            error_msg = f"無法取得初始 Prometheus 指標: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        # 獲取當前頻率
        try:
            service_info_list = await self.k8s_client.get_service_info()
            currentFrequency = get_current_frequency(service_info_list, node_name, service_type)
            if currentFrequency is None:
                error_msg = f"無法取得節點 {node_name} 上服務 {service_type} 的當前頻率"
                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
            print(f"當前頻率: {currentFrequency}")
        except Exception as e:
            if isinstance(e, RuntimeError):
                raise  # 重新拋出我們自己的錯誤
            error_msg = f"無法取得服務資訊: {e}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        # 驗證是否取得有效的 CPS 和 RPS
        if cps is None or rps is None:
            error_msg = f"無法取得有效的 CPS 或 RPS 指標，CPS: {cps}, RPS: {rps}"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
        
        max_iterations = 10  # 防止無限循環
        iteration = 0
        
        # 逐漸增加頻率直到 RPS 接近 CPS
        while (rps < cps + 5) and iteration < max_iterations:
            iteration += 1
            print(f"🔄 第 {iteration} 次迭代，當前 RPS: {rps}, CPS: {cps}")
            
            # 增加每個 agent 的頻率
            for agent in agents:
                agent_ip = agent.get("agentIP")
                agent_port = agent.get("agentPort")
                if not agent_ip or not agent_port:
                    print(f"⚠️  跳過無效的 agent 資料: {agent}")
                    continue
                
                # 每次增加 2 的頻率
                new_frequency = currentFrequency + 2
                data = {
                    'servicename': service_type,
                    "ip": 'null',
                    "port": 0,
                    "frequency": new_frequency
                }
                
                status_code, response_text = communicate_with_agent(data, agent_ip, agent_port)
                if status_code != 200:
                    print(f"⚠️  無法與 Agent {agent_ip}:{agent_port} 通信，狀態碼: {status_code}, 回應: {response_text}")
                else:
                    print(f"➡️  已通知 Agent {agent_ip}:{agent_port} 頻率更新為 {new_frequency}")
            
            # 更新頻率
            currentFrequency += 2
            
            # 等待一段時間讓變更生效
            await asyncio.sleep(3)
            
            # 重新取得指標
            try:
                cps = await prometheus_client.get_cps_by_service_and_node(service_type, node_name)
                rps = await prometheus_client.get_rps_by_service_and_node(service_type, node_name)
                print(f"更新後 CPS: {cps}, RPS: {rps}")
                
                if cps is None or rps is None:
                    error_msg = f"無法取得更新後的 Prometheus 指標，測試失敗"
                    print(f"❌ {error_msg}")
                    raise RuntimeError(error_msg)
                    
            except Exception as e:
                if isinstance(e, RuntimeError):
                    raise  # 重新拋出我們自己的錯誤
                error_msg = f"取得 Prometheus 指標時發生錯誤: {e}"
                print(f"❌ {error_msg}")
                raise RuntimeError(error_msg)
        
        # 驗證測試結果
        if cps is None:
            error_msg = f"壓力測試失敗：無法取得有效的 CPS 指標"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
            
        # 使用 CPS 作為最大吞吐量
        max_successful_frequency = int(cps)
        
        if max_successful_frequency <= 0:
            error_msg = f"壓力測試結果無效：吞吐量 {max_successful_frequency} <= 0"
            print(f"❌ {error_msg}")
            raise RuntimeError(error_msg)
            
        print(f"✅ 服務 {service_type} 測試完成，最大吞吐量: {max_successful_frequency}")
        return max_successful_frequency

    # 保持原有的單一測試方法作為備用
    async def load_test_legacy(self, deployment_hash: str) -> int:
        """舊版單一測試方法 (測試環境返回固定值)"""
        return 100


def communicate_with_agent(data: dict, agent_ip: str, agent_port: int):
    
    url = f"http://{agent_ip}:{agent_port}/servicechange"
    try:
        response = requests.post(url, data=json.dumps(data))
        print(f"communicate with Agent {agent_ip} {agent_port}, body = {data}")
        return response.status_code, response.text
    except requests.exceptions.RequestException as e:
        return None, str(e)
    
    """
    body = {
                'servicename': serviceType,
                "ip": 'null',
                "port": 0,
                "frequency": service_list[podIPIndex_dict[subscription['podIP']]['index']]['currentFrequency']
            }
            communicate_with_agent(body,str(subscription['agentIP']), int(subscription['agentPort']))
    """
    
def get_current_frequency(service_info_list, node_name: str, service_type: str):
    for service_info in service_info_list:
        if service_info.get("nodeName") == node_name and service_info.get("serviceType") == service_type:
            return service_info.get("currentFrequency")
    return None