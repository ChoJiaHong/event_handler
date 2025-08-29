import asyncio
from infra.k8s_cr_client import K8sCustomResourceClient
from repository.custom_resource_repository import ServiceRepository, SubscriptionRepository

async def main():
    # 創建 K8s 客戶端
    client = K8sCustomResourceClient()
    
    # 建立 repository 實例
    service_repo = ServiceRepository(client, namespace="default")
    subscription_repo = SubscriptionRepository(client, namespace="arha-system")

    # 取得服務資訊
    service_info = await service_repo.get_service_info()
    if service_info:
        print("=== Service Info ===")
        print(service_info)
    else:
        print("❌ No service info available")
    
    # 列舉所有服務
    services = await service_repo.list_services()
    print(f"Found {len(services)} services.")

    # 取得訂閱資訊
    subscription_info = await subscription_repo.get_subscription_info()
    if subscription_info:
        print("=== Subscription Info ===")
        print(subscription_info)
    else:
        print("❌ No subscription info available")

    # 範例：更新服務頻率(假設 frequencies 為 {service_type: frequency})
    frequencies = {"pose": 20, "gesture": 30}
    update_result = await service_repo.update_service_frequencies(frequencies)
    print(f"Update frequencies result: {update_result}")

    # 範例：刪除指定服務 (請更換為存在的服務名稱)
    delete_result = await service_repo.delete_service("example-service")
    print(f"Delete service result: {delete_result}")

    # 範例：刪除指定訂閱 (請更換為存在的訂閱名稱)
    delete_sub_result = await subscription_repo.delete_subscription("example-subscription")
    print(f"Delete subscription result: {delete_sub_result}")

if __name__ == "__main__":
    asyncio.run(main())