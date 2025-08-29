import asyncio
from infra.k8s_subscription_client import CrdRepository
import utils.subscription_analysis as analysis_utils


async def basic_usage_example():
    """基本使用範例"""
    print("=== 基本使用範例 ===")
    
    # 創建客戶端
    client = CrdRepository()
    
    # 檢查客戶端狀態
    if hasattr(client, 'custom_api') and client.custom_api is not None:
        print("✓ Kubernetes API 客戶端初始化成功")
    else:
        print("⚠️  使用 stub 資料（無 Kubernetes 連接）")
    
    # 獲取訂閱資訊
    try:
        subscription_info = await client.get_subscription_info()
        
        if subscription_info:
            print("✓ 成功獲取訂閱資訊")
            print(f"資料類型: {type(subscription_info)}")
            print(f"資料內容: {subscription_info}")
            
            # 解析 agents
            raw_agents = subscription_info.get('raw', [])
            print(f"純內容： {raw_agents}")
            print(f"總 agents 數量: {len(raw_agents)}")
            
            # 使用分析工具函式產生分析結果字串
            analysis = analysis_utils.analyze_subscription_info(subscription_info)
            analysis_str = analysis_utils.get_subscription_analysis_str(analysis, raw_agents)
            print("\n=== 分析結果 ===")
            print(analysis_str)
            
            return subscription_info
        else:
            print("❌ 獲取訂閱資訊失敗或為空")
            return None
            
    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
        return None

async def detailed_analysis_example():
    """詳細分析訂閱資料的範例"""
    print("\n=== 詳細分析範例 ===")
    
    client = CrdRepository()
    subscription_info = await client.get_subscription_info()
    
    if not subscription_info:
        print("❌ 無法獲取訂閱資訊")
        return
    
    analysis = analysis_utils.analyze_subscription_info(subscription_info)
    analysis_str = analysis_utils.get_subscription_analysis_str(analysis, subscription_info.get("raw", []))
    print(analysis_str)
    
async def da():
    client = CrdRepository()
    
    # 取得訂閱資訊
    subscription_info = await client.get_subscription_info()
    print("=== Subscription Info ===")
    print(subscription_info)
    
    # 取得服務資訊
    service_info = await client.get_service_info()
    print("\n=== Service Info ===")
    print(service_info)
    
    # 取得服務規格資訊 (ServiceSpec)
    service_spec_info = await client.get_service_spec_info()
    print("\n=== ServiceSpec Info ===")
    print(service_spec_info)
    
            
async def main():
    #await detailed_analysis_example()
    #await basic_usage_example()
    await da()
if __name__ == "__main__":
    asyncio.run(main())