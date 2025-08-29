import asyncio
from typing import Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class CrdRepository:
    """專門處理 Kubernetes 訂閱資訊的客戶端"""
    
    def __init__(self):
        try:
            config.load_incluster_config()
            self.custom_api = client.CustomObjectsApi()
        except Exception:
            try:
                config.load_kube_config()
                self.custom_api = client.CustomObjectsApi()
            except Exception:
                # 在測試或缺少配置時，使用 None 並提供 stub 資料
                self.custom_api = None
                self._stub = {"spec": {"raw": [{"id": "agent"}]}}

    async def get_subscription_info(self) -> Dict[str, Any]:
        """
        獲取訂閱資訊

        範例 output:
        [
          {'agentIP': '10.52.52.111', 'agentPort': 8896, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.37', 'serviceType': 'gesture'},
          {'agentIP': '10.52.52.111', 'agentPort': 8897, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.38', 'serviceType': 'pose'},
          {'agentIP': '10.52.52.111', 'agentPort': 8897, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.37', 'serviceType': 'gesture'},
          {'agentIP': '10.52.52.111', 'agentPort': 8898, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.37', 'serviceType': 'gesture'},
          {'agentIP': '10.52.52.111', 'agentPort': 8899, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.38', 'serviceType': 'pose'},
          {'agentIP': '10.52.52.111', 'agentPort': 8899, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.37', 'serviceType': 'gesture'},
          {'agentIP': '10.52.52.111', 'agentPort': 9250, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.37', 'serviceType': 'gesture'},
          {'agentIP': '10.52.52.111', 'agentPort': 9251, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.38', 'serviceType': 'pose'},
          {'agentIP': '10.52.52.111', 'agentPort': 9251, 'nodeName': 'workgpu', 
           'podIP': '10.244.2.37', 'serviceType': 'gesture'}
        ]
        """
        if not getattr(self, "custom_api", None):
            return self._stub.get("spec", {}) if hasattr(self, "_stub") else {}
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.get_namespaced_custom_object,
                "ha.example.com", "v1", "arha-system", "subscriptions", "subscription-info"
            )
            return response.get('spec', {}).get('raw', [])
        except (ApiException, Exception):
            return {}
        
    async def get_service_info(self) -> Dict[str, Any]:
        """
        獲取服務資訊

        範例 output:
        [
          {
            'currentConnection': 6, 
            'currentFrequency': 15, 
            'frequencyLimit': [30, 15],
            'hostIP': '10.52.52.25', 
            'hostPort': 30501, 
            'nodeName': 'workgpu', 
            'podIP': '10.244.2.37', 
            'serviceType': 'gesture', 
            'workloadLimit': 90
          },
          {
            'currentConnection': 3, 
            'currentFrequency': 11, 
            'frequencyLimit': [20, 10],
            'hostIP': '10.52.52.25', 
            'hostPort': 30502, 
            'nodeName': 'workgpu', 
            'podIP': '10.244.2.38', 
            'serviceType': 'pose', 
            'workloadLimit': 33
          }
        ]
        """
        if not getattr(self, "custom_api", None):
            return self._stub.get("spec", {}) if hasattr(self, "_stub") else {}
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.get_namespaced_custom_object,
                "ha.example.com", "v1", "arha-system", "services", "service-info"
            )
            return response.get('spec', {}).get('raw', [])
        except (ApiException, Exception):
            return {}
        
    async def get_service_spec_info(self) -> Any:
        """
        取得 ServiceSpec 中 raw 的值

        範例 output:
        [
          {
            'frequencyLimit': [30, 15], 
            'gpuMemoryRequest': 1, 
            'serviceType': 'gesture', 
            'workAbility': {'pdclab': 230, 'workgpu': 180}
          },
          {
            'frequencyLimit': [20, 10], 
            'gpuMemoryRequest': 1, 
            'serviceType': 'pose', 
            'workAbility': {'pdclab': 80, 'workgpu': 66}
          }
        ]
        """
        if not getattr(self, "custom_api", None):
            return self._stub.get("spec", {}) if hasattr(self, "_stub") else {}
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.get_namespaced_custom_object,
                "ha.example.com",      # API Group
                "v1",                  # API Version
                "arha-system",         # Namespace
                "servicespecs",        # plural: servicespecs
                "servicespec-info"     # 資源名稱
            )
            return response.get("spec", {}).get("raw", [])
        except (ApiException, Exception):
            return {}

