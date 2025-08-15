import asyncio
import json
from typing import Any, Dict, List, Optional
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException
from shared.logger import get_logger

logger = get_logger(__name__)

class K8sCustomResourceClient:
    """Kubernetes CustomResource 讀寫客戶端"""
    
    def __init__(self):
        """
        初始化 Kubernetes client
        
        Side Effects:
        - 載入 Kubernetes 配置 (叢集內或本地)
        - 建立 CustomObjectsApi client
        """
        try:
            # 嘗試載入叢集內配置
            config.load_incluster_config()
            logger.info("已載入叢集內 Kubernetes 配置")
        except ConfigException:
            try:
                # 如果不在叢集內，則載入本地配置
                config.load_kube_config()
                logger.info("已載入本地 Kubernetes 配置")
            except ConfigException:
                logger.warning("無法載入 Kubernetes 配置，部分功能將不可用")
                self.custom_api = None
                self.core_api = None
                return

        self.custom_api = client.CustomObjectsApi()
        self.core_api = client.CoreV1Api()

    async def get_custom_resource(
        self,
        group: str,
        version: str,
        namespace: str,
        plural: str,
        name: str
    ) -> Optional[Dict[str, Any]]:
        """
        讀取指定的 CustomResource
        
        Input:
        - group: API group，例如 "ha.example.com"
        - version: API version，例如 "v1"
        - namespace: namespace 名稱
        - plural: 資源複數名稱，例如 "services"
        - name: 資源名稱
        
        Output:
        - Dict[str, Any]: CustomResource 的完整內容，包含 metadata, spec, status
        - None: 如果資源不存在或讀取失敗
        """
        if not self.custom_api:
            return None
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.get_namespaced_custom_object,
                group,
                version,
                namespace,
                plural,
                name,
            )
            logger.info(f"成功讀取 CR: {namespace}/{name}")
            return response

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"CustomResource 不存在: {namespace}/{name}")
            else:
                logger.error(f"讀取 CustomResource 失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"執行 Kubernetes API 時發生錯誤: {e}")
            return None

    async def list_custom_resources(
        self,
        group: str,
        version: str,
        namespace: str,
        plural: str,
        label_selector: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        列出指定類型的所有 CustomResources
        
        Input:
        - group: API group
        - version: API version
        - namespace: namespace 名稱
        - plural: 資源複數名稱
        - label_selector: 可選的標籤選擇器，例如 "app=myapp"
        
        Output:
        - List[Dict[str, Any]]: CustomResource 列表
        """
        if not self.custom_api:
            return []
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.custom_api.list_namespaced_custom_object(
                    group,
                    version,
                    namespace,
                    plural,
                    label_selector=label_selector,
                ),
            )
            items = response.get('items', [])
            logger.info(f"成功列出 {len(items)} 個 CustomResources")
            return items

        except ApiException as e:
            logger.error(f"列出 CustomResources 失敗: {e}")
            return []
        except Exception as e:
            logger.error(f"執行 Kubernetes API 時發生錯誤: {e}")
            return []

    async def create_custom_resource(
        self,
        group: str,
        version: str,
        namespace: str,
        plural: str,
        body: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        創建新的 CustomResource
        
        Input:
        - group: API group
        - version: API version
        - namespace: namespace 名稱
        - plural: 資源複數名稱
        - body: CustomResource 的完整定義
        
        Output:
        - Dict[str, Any]: 創建成功的 CustomResource
        - None: 如果創建失敗
        """
        if not self.custom_api:
            return None
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.create_namespaced_custom_object,
                group,
                version,
                namespace,
                plural,
                body,
            )
            name = body.get('metadata', {}).get('name', 'unknown')
            logger.info(f"成功創建 CR: {namespace}/{name}")
            return response

        except ApiException as e:
            logger.error(f"創建 CustomResource 失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"執行 Kubernetes API 時發生錯誤: {e}")
            return None

    async def update_custom_resource(
        self,
        group: str,
        version: str,
        namespace: str,
        plural: str,
        name: str,
        body: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        更新現有的 CustomResource
        
        Input:
        - group: API group
        - version: API version
        - namespace: namespace 名稱
        - plural: 資源複數名稱
        - name: 資源名稱
        - body: 更新後的 CustomResource 定義
        
        Output:
        - Dict[str, Any]: 更新成功的 CustomResource
        - None: 如果更新失敗
        """
        if not self.custom_api:
            return None
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.replace_namespaced_custom_object,
                group,
                version,
                namespace,
                plural,
                name,
                body,
            )
            logger.info(f"成功更新 CR: {namespace}/{name}")
            return response

        except ApiException as e:
            logger.error(f"更新 CustomResource 失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"執行 Kubernetes API 時發生錯誤: {e}")
            return None

    async def patch_custom_resource(
        self,
        group: str,
        version: str,
        namespace: str,
        plural: str,
        name: str,
        patch: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        部分更新 CustomResource (JSON Merge Patch)
        
        Input:
        - group: API group
        - version: API version
        - namespace: namespace 名稱
        - plural: 資源複數名稱
        - name: 資源名稱
        - patch: 要更新的欄位
        
        Output:
        - Dict[str, Any]: 更新成功的 CustomResource
        - None: 如果更新失敗
        """
        if not self.custom_api:
            return None
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self.custom_api.patch_namespaced_custom_object,
                group,
                version,
                namespace,
                plural,
                name,
                patch,
            )
            logger.info(f"成功 patch CR: {namespace}/{name}")
            return response

        except ApiException as e:
            logger.error(f"Patch CustomResource 失敗: {e}")
            return None
        except Exception as e:
            logger.error(f"執行 Kubernetes API 時發生錯誤: {e}")
            return None

    async def delete_custom_resource(
        self,
        group: str,
        version: str,
        namespace: str,
        plural: str,
        name: str
    ) -> bool:
        """
        刪除 CustomResource
        
        Input:
        - group: API group
        - version: API version
        - namespace: namespace 名稱
        - plural: 資源複數名稱
        - name: 資源名稱
        
        Output:
        - bool: 刪除是否成功
        """
        if not self.custom_api:
            return False
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                self.custom_api.delete_namespaced_custom_object,
                group,
                version,
                namespace,
                plural,
                name,
            )
            logger.info(f"成功刪除 CR: {namespace}/{name}")
            return True

        except ApiException as e:
            if e.status == 404:
                logger.warning(f"CustomResource 不存在，無法刪除: {namespace}/{name}")
            else:
                logger.error(f"刪除 CustomResource 失敗: {e}")
            return False
        except Exception as e:
            logger.error(f"執行 Kubernetes API 時發生錯誤: {e}")
            return False

    # 便利方法：針對您專案中的特定 CustomResources
    async def get_service_info(self, namespace: str = "default") -> Optional[Dict[str, Any]]:
        """獲取服務資訊 CustomResource"""
        return await self.get_custom_resource(
            "ha.example.com", "v1", namespace, "services", "service-info"
        )

    async def get_subscription_info(self, namespace: str = "arha-system") -> Optional[Dict[str, Any]]:
        """獲取訂閱資訊 CustomResource"""
        return await self.get_custom_resource(
            "ha.example.com", "v1", namespace, "subscriptions", "subscription-info"
        )

    async def update_service_frequencies(
        self, 
        frequencies: Dict[str, int], 
        namespace: str = "default"
    ) -> bool:
        """
        更新服務頻率
        
        Input:
        - frequencies: {service_type: frequency} 的字典
        - namespace: namespace 名稱
        
        Output:
        - bool: 更新是否成功
        """
        # 首先獲取當前的服務資訊
        current = await self.get_service_info(namespace)
        if not current:
            logger.error("無法獲取當前服務資訊")
            return False

        # 更新頻率
        updated_raw = []
        for item in current.get('spec', {}).get('raw', []):
            service_type = item.get('serviceType')
            if service_type in frequencies:
                item = item.copy()  # 避免修改原始資料
                item['currentFrequency'] = frequencies[service_type]
            updated_raw.append(item)

        # 準備 patch
        patch = {
            'spec': {
                'raw': updated_raw
            }
        }

        # 執行更新
        result = await self.patch_custom_resource(
            "ha.example.com", "v1", namespace, "services", "service-info", patch
        )
        
        return result is not None