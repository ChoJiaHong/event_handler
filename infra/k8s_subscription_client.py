import asyncio
from typing import Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class K8sSubscriptionClient:
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
        """獲取訂閱資訊"""
        if not getattr(self, "custom_api", None):
            return self._stub.get("spec", {}) if hasattr(self, "_stub") else {}
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.get_namespaced_custom_object,
                "ha.example.com", "v1", "arha-system", "subscriptions", "subscription-info"
            )
            return response.get('spec', {})
        except (ApiException, Exception):
            return {}
