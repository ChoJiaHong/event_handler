

---

# Event Handler

本專案提供一個極簡的事件處理中心（Event Processing Center）實作，依據軟體需求規格（SRS）設計。`EventProcessor` 會將進來的事件路由給已註冊的 handler，同時協調周邊服務。目前範例只包含 `DeploymentChangeHandler`。

---

## 事件處理設計

* **事件處理（EventProcessor）**：負責接收並分發事件給對應的 Handler。
* **Handler 擴充**：所有 Handler 與外部觸發（如 operator）完全解耦，易於擴展。

---

## Throughput Key 支援

`ThroughputRecorder` 操作接受兩種 key 格式：

* 傳統字串格式
* 字典格式，內容包含 `node` 和 `services` 欄位

**範例：**

```python
deployment = {"node": "node1", "services": {"pose": 1, "gesture": 2}}
await recorder.save(deployment, 100, "pose")
```

無論字典順序如何，系統內部都會轉為標準 key 進行查詢，查找時順序不影響結果。

---

## Kopf Operator 集成

[**Kopf**](https://kopf.readthedocs.io/) 可用於從 Kubernetes 觸發領域事件。
`infra/kopf_operator.py` 中的 operator 會監聽 group `example.com` 下的 `Event` custom resource，並將其轉換為領域事件傳給 `EventProcessor`。

### 運行 Operator

```bash
pip install kopf
kopf run infra/kopf_operator.py
```

建立 custom resource 時，填入 `spec.type` 與 `spec.payload` 欄位，即會觸發領域事件，所有已註冊 Handler 皆會收到此事件。

---

## Handler 擴展範例

Handler 擴充完全獨立於 operator。
要增加新的事件類型，請參考以下寫法：

```python
from handlers.base import BaseHandler

class ScaleUpHandler(BaseHandler):
    async def handle(self, event, ctx):
        # 自訂邏輯

processor.register_handler("SCALE_UP", ScaleUpHandler())
```

---

## 執行測試

```bash
pytest -q
```

