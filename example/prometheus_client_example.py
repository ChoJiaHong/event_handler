"""
PrometheusClient 使用範例

這個範例展示如何使用 PrometheusClient 來查詢 Prometheus 指標資料，
並進行基本的監控和資料處理。
"""

import asyncio
import json
from typing import Dict, List, Any


from infra.prometheus_client import PrometheusClient
import asyncio
from prometheus_api_client import PrometheusConnect

async def basic_prometheus_example():
    """基本 PrometheusClient 使用範例"""
    print("=== PrometheusClient 基本使用範例 ===\n")

    # 建立 PrometheusClient 實例
    client = PrometheusConnect(
        url="http://prometheus-operated.prometheus.svc.cluster.local:9090",
        disable_ssl=True
    )


    # 設定 node_name 與 service_type
    node_name = "workgpu"
    service_type = "gesture"

    # PromQL：直接用 pod 名稱 (service-type + node-name)
    pod_name = f"{service_type}-{node_name}-30501"
    query = f'requests_per_second{{job="default/pose-podmonitor", pod="{pod_name}"}}'

    print(f"查詢 pod={pod_name} 的 RPS …\n")
    result = client.custom_query(query=query)

    if not result:
        print("⚠️ 沒有查到資料，請確認 pod 名稱正確 & metric 有輸出")
    else:
        print("📊 成功取得 RPS 數據：")
        for series in result:
            metric = series["metric"]
            ts, value = series["value"]
            
            # 提取關鍵資訊
            pod_name = metric.get("pod", "unknown")
            container = metric.get("container", "unknown")
            instance = metric.get("instance", "unknown")
            rps_value = float(value)
            
            print(f"  🔹 Pod: {pod_name}")
            print(f"  🔹 Container: {container}")
            print(f"  🔹 Instance: {instance}")
            print(f"  🔹 當前 RPS: {rps_value} 次/秒")
            print(f"  🔹 時間戳: {ts}")
            print()
async def detailed_prometheus_example():
    client = PrometheusClient()
    #metrics = await client.get_rps_by_service_and_node("gesture", "workgpu", "30501")
    metrics = await client.get_cps_by_service_and_node("gesture", "workgpu")
    
    print("=== PrometheusClient 詳細使用範例 ===\n")
    print(json.dumps(metrics, indent=2))

async def main():
    """主函式，執行所有範例"""
    print("PrometheusClient 使用範例集合")
    print("=" * 60)
    
    try:
        #await basic_prometheus_example()
        await detailed_prometheus_example()
    except KeyboardInterrupt:
        print("\n程式被使用者中斷")
    except Exception as e:
        print(f"\n執行錯誤: {e}")
    
    print("\n" + "=" * 60)
    print("所有範例執行完成！")


if __name__ == "__main__":
    # 執行範例
    asyncio.run(main())
