"""
Infra PrometheusClient 使用範例

展示如何使用 infra.prometheus_client 模組來查詢指定節點和服務類型的指標
"""

import asyncio
import sys
import os

# 添加 event_handler 到 Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from infra.prometheus_client import PrometheusClient


async def example_get_rps():
    """範例：取得指定服務和節點的 RPS"""
    print("=== 取得 RPS 指標範例 ===")
    
    client = PrometheusClient()
    
    # 查詢特定 Pod 的 RPS
    service_type = "gesture"
    node_name = "workgpu"
    port_suffix = "30501"
    
    print(f"🔍 查詢 {service_type} 服務在 {node_name} 節點 (port {port_suffix}) 的 RPS...")
    rps = await client.get_rps_by_service_and_node(service_type, node_name, port_suffix)
    
    if rps is not None:
        print(f"📊 RPS: {rps:.2f} 次/秒")
    else:
        print(f"❌ 找不到 {service_type}-{node_name}-{port_suffix} 的 RPS 資料")
    
    # 查詢該服務類型在該節點的任何 Pod
    print(f"\n🔍 查詢 {service_type} 服務在 {node_name} 節點 (任何 port) 的 RPS...")
    rps_any = await client.get_rps_by_service_and_node(service_type, node_name)
    
    if rps_any is not None:
        print(f"📊 RPS: {rps_any:.2f} 次/秒")
    else:
        print(f"❌ 找不到 {service_type} 在 {node_name} 節點的任何 RPS 資料")


async def example_get_all_metrics():
    """範例：取得指定服務和節點的所有指標"""
    print("\n=== 取得所有指標範例 ===")
    
    client = PrometheusClient()
    
    service_type = "gesture"
    node_name = "workgpu"
    port_suffix = "30501"
    
    print(f"🔍 取得 {service_type} 服務在 {node_name} 節點的完整指標...")
    metrics = await client.get_all_metrics_by_service_and_node(service_type, node_name, port_suffix)
    
    print(f"📋 完整指標:")
    print(f"   🔹 Pod 名稱: {metrics.get('pod_name', 'N/A')}")
    print(f"   🔹 服務類型: {metrics.get('service_type', 'N/A')}")
    print(f"   🔹 節點名稱: {metrics.get('node_name', 'N/A')}")
    print(f"   🔹 RPS: {metrics.get('rps', 'N/A')} 次/秒")
    print(f"   🔹 GPU 使用率: {metrics.get('gpu_utilization', 'N/A')}%")
    print(f"   🔹 記憶體使用量: {metrics.get('memory_usage_mb', 'N/A')} MB")


async def example_get_all_pods_by_service():
    """範例：取得指定服務類型的所有 Pod"""
    print("\n=== 取得服務類型所有 Pod 範例 ===")
    
    client = PrometheusClient()
    
    service_type = "gesture"
    print(f"🔍 搜尋所有 {service_type} 服務的 Pod...")
    pods = await client.get_pods_by_service_type(service_type)
    
    if pods:
        print(f"🎯 找到 {len(pods)} 個 {service_type} 服務的 Pod:")
        for pod in pods:
            print(f"   📦 {pod['pod_name']}")
            print(f"      ├── 節點: {pod['node_name']}")
            print(f"      ├── 端口: {pod['port']}")
            print(f"      ├── 實例: {pod['instance']}")
            print(f"      └── 當前 RPS: {pod['current_rps']:.2f}")
    else:
        print(f"❌ 找不到任何 {service_type} 服務的 Pod")


async def example_compare_nodes():
    """範例：比較不同節點上同類型服務的效能"""
    print("\n=== 節點效能比較範例 ===")
    
    client = PrometheusClient()
    
    service_type = "gesture"
    nodes = ["workgpu", "workergpu2"]  # 假設有這兩個節點
    
    print(f"🔄 比較 {service_type} 服務在不同節點的效能:")
    
    for node in nodes:
        print(f"\n   🖥️  節點: {node}")
        metrics = await client.get_all_metrics_by_service_and_node(service_type, node)
        
        if metrics.get('rps') is not None:
            print(f"      ├── RPS: {metrics['rps']:.2f} 次/秒")
            if metrics.get('gpu_utilization') is not None:
                print(f"      ├── GPU 使用率: {metrics['gpu_utilization']:.1f}%")
            else:
                print(f"      ├── GPU 使用率: N/A")
            if metrics.get('memory_usage_mb') is not None:
                print(f"      └── 記憶體使用量: {metrics['memory_usage_mb']:.1f} MB")
            else:
                print(f"      └── 記憶體使用量: N/A")
        else:
            print(f"      └── ❌ 無資料")


async def main():
    """主函式"""
    print("🚀 Infra PrometheusClient 使用範例")
    print("=" * 60)
    
    try:
        await example_get_rps()
        await example_get_all_metrics()
        await example_get_all_pods_by_service()
        await example_compare_nodes()
        
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✅ 所有範例執行完成！")


if __name__ == "__main__":
    asyncio.run(main())
