from typing import Any, Dict, List, Optional
from infra.k8s_cr_client import K8sCustomResourceClient

class ServiceRepository:
    """
    封裝與服務相關的 CustomResource 操作
    """
    def __init__(self, client: K8sCustomResourceClient, namespace: str = "default"):
        self.client = client
        self.namespace = namespace

    async def get_service_info(self) -> Optional[Dict[str, Any]]:
        """獲取服務資訊"""
        return await self.client.get_service_info(self.namespace)

    async def list_services(self) -> List[Dict[str, Any]]:
        """列舉所有服務 CustomResource（假設 plural 為 services）"""
        return await self.client.list_custom_resources(
            "ha.example.com", "v1", self.namespace, "services"
        )

    async def update_service_frequencies(self, frequencies: Dict[str, int]) -> bool:
        """更新服務頻率"""
        return await self.client.update_service_frequencies(frequencies, self.namespace)

    async def delete_service(self, name: str) -> bool:
        """刪除指定的服務 CustomResource"""
        return await self.client.delete_custom_resource(
            "ha.example.com", "v1", self.namespace, "services", name
        )

class SubscriptionRepository:
    """
    封裝與訂閱相關的 CustomResource 操作
    """
    def __init__(self, client: K8sCustomResourceClient, namespace: str = "arha-system"):
        self.client = client
        self.namespace = namespace

    async def get_subscription_info(self) -> Optional[Dict[str, Any]]:
        """獲取訂閱資訊"""
        return await self.client.get_subscription_info(self.namespace)

    async def delete_subscription(self, name: str) -> bool:
        """刪除指定的訂閱 CustomResource"""
        return await self.client.delete_custom_resource(
            "ha.example.com", "v1", self.namespace, "subscriptions", name
        )