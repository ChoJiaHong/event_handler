import asyncio
from infrastructure.k8s_cr_client import K8sCustomResourceClient


def test_k8s_cr_client_operations():
    """測試 K8s CustomResource 客戶端的基本操作"""

    async def run():
        client = K8sCustomResourceClient()

        # 測試獲取服務資訊
        service_info = await client.get_service_info()
        if service_info:
            assert 'spec' in service_info
            assert 'metadata' in service_info
            print(f"獲取到服務資訊: {service_info.get('metadata', {}).get('name')}")

        # 測試獲取訂閱資訊
        subscription_info = await client.get_subscription_info()
        if subscription_info:
            assert 'spec' in subscription_info
            print(f"獲取到訂閱資訊: {subscription_info.get('metadata', {}).get('name')}")

        # 測試列出資源
        services = await client.list_custom_resources(
            "ha.example.com", "v1", "default", "services"
        )
        print(f"找到 {len(services)} 個服務資源")

    asyncio.run(run())