import asyncio
from typing import Dict, Any
from kubernetes import client, config
from kubernetes.client.rest import ApiException

class K8sSubscriptionClient:
    """專門處理 Kubernetes 訂閱資訊的客戶端"""
    
    def __init__(self):
        try:
            config.load_incluster_config()
        except:
            config.load_kube_config()
        self.custom_api = client.CustomObjectsApi()

    async def get_subscription_info(self) -> Dict[str, Any]:
        """獲取訂閱資訊"""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.get_namespaced_custom_object,
                "ha.example.com", "v1", "arha-system", "subscriptions", "subscription-info"
            )
            return response.get('spec', {})
        except (ApiException, Exception) as e:
            print(f"獲取訂閱資訊失敗: {e}")
            return {}