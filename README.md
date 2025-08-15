# Event Handler

此專案提供一個簡化的事件驅動範例。程式碼依照業務功能劃分為 `features/<module>`，每個模組皆包含 `domain/`、`application/` 與 `infrastructure/` 三層，並以 `domain/aggregate.py` 作為聚合根的公開入口。

```
features/
├── deployment/
│   ├── domain/
│   └── infrastructure/
└── throughput/
    ├── domain/
    ├── application/
    └── infrastructure/
```

共用的工具與介面移至 `shared/`，提供統一的 logger、設定與驗證器，以及其他可重用的協助函式：

```
shared/
├── config.py
├── event.py
├── helpers.py
├── logger.py
├── service_lookup.py
└── validators.py
```

## 事件總線

模組之間透過 `event_bus` 溝通，使用 `publish()` 與 `subscribe()` 介面註冊或傳遞事件：

```python
from event_bus import publish, subscribe
from shared.event import Event

async def handler(event: Event):
    ...

subscribe("EXAMPLE", handler)
await publish(Event(type="EXAMPLE", payload={}, timestamp=datetime.utcnow(), source="test"))
```

Throughput 模組的應用層會在啟動時向事件總線註冊 handlers，聚合根提供 `register(ctx)` 方法進行註冊。`app/main.py` 負責組裝相依性並啟動事件流。

## 測試

測試依照模組放置於 `tests/features/<module>` 或 `tests/shared`。執行所有測試：

```bash
pytest -q
```

