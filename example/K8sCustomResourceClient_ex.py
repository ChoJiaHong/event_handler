import asyncio
import json
from infra.k8s_cr_client import K8sCustomResourceClient


async def test_k8s_cr_client():
    """測試 K8sCustomResourceClient 的各種功能"""
    print("=== K8sCustomResourceClient 測試 ===\n")
    
    # 創建客戶端
    client = K8sCustomResourceClient()
    
    # 檢查客戶端狀態
    if client.custom_api is not None:
        print("✅ Kubernetes API 客戶端初始化成功")
    else:
        print("❌ Kubernetes API 客戶端初始化失敗，無法繼續測試")
        return
    
    print("\n1. 測試獲取服務資訊 (service-info)")
    print("-" * 50)
    
    # 測試獲取服務資訊 (在 arha-system namespace)
    service_info = await client.get_service_info("arha-system")
    if service_info:
        print("✅ 成功獲取服務資訊")
        print(f"資源名稱: {service_info.get('metadata', {}).get('name')}")
        print(f"命名空間: {service_info.get('metadata', {}).get('namespace')}")
        print(f"資源版本: {service_info.get('metadata', {}).get('resourceVersion')}")
        
        # 分析 spec 內容
        spec = service_info.get('spec', {})
        raw_services = spec.get('raw', [])
        print(f"服務數量: {len(raw_services)}")
        
        for i, service in enumerate(raw_services):
            print(f"  服務 {i+1}:")
            print(f"    當前連接: {service.get('currentConnection', 'N/A')}")
            print(f"    當前頻率: {service.get('currentFrequency', 'N/A')}")
            print(f"    負載限制: {service.get('workloadLimit', 'N/A')}")
    else:
        print("❌ 無法獲取服務資訊")
    
    print("\n2. 測試獲取訂閱資訊 (subscription-info)")
    print("-" * 50)
    
    # 測試獲取訂閱資訊
    subscription_info = await client.get_subscription_info()
    if subscription_info:
        print("✅ 成功獲取訂閱資訊")
        print(f"資源名稱: {subscription_info.get('metadata', {}).get('name')}")
        print(f"命名空間: {subscription_info.get('metadata', {}).get('namespace')}")
        
        # 分析 agents
        spec = subscription_info.get('spec', {})
        raw_agents = spec.get('raw', [])
        print(f"總 agents 數量: {len(raw_agents)}")
        
        # 統計分析
        service_stats = {}
        node_stats = {}
        
        for agent in raw_agents:
            service_type = agent.get('serviceType', 'unknown')
            node_name = agent.get('nodeName', 'unknown')
            
            service_stats[service_type] = service_stats.get(service_type, 0) + 1
            node_stats[node_name] = node_stats.get(node_name, 0) + 1
        
        print("\n服務類型分布:")
        for service_type, count in service_stats.items():
            print(f"  {service_type}: {count} agents")
        
        print("\n節點分布:")
        for node_name, count in node_stats.items():
            print(f"  {node_name}: {count} agents")
        
        print("\n前 3 個 agents 詳細資訊:")
        for i, agent in enumerate(raw_agents[:3]):
            print(f"  Agent {i+1}:")
            print(f"    IP: {agent.get('agentIP')}")
            print(f"    Port: {agent.get('agentPort')}")
            print(f"    Service: {agent.get('serviceType')}")
            print(f"    Node: {agent.get('nodeName')}")
            print(f"    Pod IP: {agent.get('podIP')}")
    else:
        print("❌ 無法獲取訂閱資訊")
    
    print("\n3. 測試列出所有服務資源")
    print("-" * 50)
    
    # 列出所有服務
    services = await client.list_custom_resources(
        "ha.example.com", "v1", "arha-system", "services"
    )
    print(f"找到 {len(services)} 個服務資源:")
    for service in services:
        name = service.get('metadata', {}).get('name')
        print(f"  - {name}")
    
    print("\n4. 測試列出所有訂閱資源")
    print("-" * 50)
    
    # 列出所有訂閱
    subscriptions = await client.list_custom_resources(
        "ha.example.com", "v1", "arha-system", "subscriptions"
    )
    print(f"找到 {len(subscriptions)} 個訂閱資源:")
    for subscription in subscriptions:
        name = subscription.get('metadata', {}).get('name')
        print(f"  - {name}")
    
    print("\n5. 測試獲取 ServiceSpec 資訊")
    print("-" * 50)
    
    # 嘗試獲取 ServiceSpec
    servicespec_info = await client.get_custom_resource(
        "ha.example.com", "v1", "arha-system", "servicespecs", "servicespec-info"
    )
    if servicespec_info:
        print("✅ 成功獲取 ServiceSpec 資訊")
        spec = servicespec_info.get('spec', {})
        raw_specs = spec.get('raw', [])
        print(f"ServiceSpec 數量: {len(raw_specs)}")
        
        for i, spec_item in enumerate(raw_specs):
            print(f"  Spec {i+1}:")
            print(f"    服務類型: {spec_item.get('serviceType')}")
            print(f"    頻率限制: {spec_item.get('frequencyLimit')}")
            print(f"    GPU 記憶體需求: {spec_item.get('gpuMemoryRequest')}")
            print(f"    工作能力: {spec_item.get('workAbility')}")
    else:
        print("❌ 無法獲取 ServiceSpec 資訊")


async def test_data_export():
    """將獲取的資料匯出到檔案"""
    print("\n=== 資料匯出測試 ===")
    
    client = K8sCustomResourceClient()
    
    if not client.custom_api:
        print("❌ API 客戶端未初始化")
        return
    
    # 收集所有資料
    data = {}
    
    print("正在收集資料...")
    
    # 獲取服務資訊
    service_info = await client.get_service_info("arha-system")
    if service_info:
        data['service_info'] = service_info
        print("✅ 服務資訊已收集")
    
    # 獲取訂閱資訊
    subscription_info = await client.get_subscription_info()
    if subscription_info:
        data['subscription_info'] = subscription_info
        print("✅ 訂閱資訊已收集")
    
    # 獲取 ServiceSpec 資訊
    servicespec_info = await client.get_custom_resource(
        "ha.example.com", "v1", "arha-system", "servicespecs", "servicespec-info"
    )
    if servicespec_info:
        data['servicespec_info'] = servicespec_info
        print("✅ ServiceSpec 資訊已收集")
    
    # 儲存到檔案
    if data:
        filename = 'k8s_cr_data_export.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"✅ 資料已匯出到 {filename}")
        
        # 簡單統計
        print("\n匯出資料統計:")
        if 'service_info' in data:
            services = data['service_info'].get('spec', {}).get('raw', [])
            print(f"  服務: {len(services)} 個")
        
        if 'subscription_info' in data:
            agents = data['subscription_info'].get('spec', {}).get('raw', [])
            print(f"  Agents: {len(agents)} 個")
        
        if 'servicespec_info' in data:
            specs = data['servicespec_info'].get('spec', {}).get('raw', [])
            print(f"  ServiceSpecs: {len(specs)} 個")
    else:
        print("❌ 沒有資料可以匯出")


async def test_error_handling():
    """測試錯誤處理"""
    print("\n=== 錯誤處理測試 ===")
    
    client = K8sCustomResourceClient()
    
    # 測試不存在的資源
    print("1. 測試獲取不存在的資源...")
    non_existent = await client.get_custom_resource(
        "ha.example.com", "v1", "arha-system", "services", "non-existent-service"
    )
    if non_existent is None:
        print("✅ 正確處理不存在的資源")
    else:
        print("❌ 錯誤處理失敗")
    
    # 測試無效的 API group
    print("2. 測試無效的 API group...")
    invalid_group = await client.list_custom_resources(
        "invalid.group.com", "v1", "arha-system", "services"
    )
    if not invalid_group:
        print("✅ 正確處理無效的 API group")
    else:
        print("❌ 錯誤處理失敗")


async def main():
    """主函數"""
    try:
        # 運行基本測試
        await test_k8s_cr_client()
        
        # 運行資料匯出
        await test_data_export()
        
        # 運行錯誤處理測試
        await test_error_handling()
        
        print("\n🎉 所有測試完成！")
        
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())