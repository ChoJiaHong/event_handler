from collections import Counter
from typing import Dict, Any, Tuple

def _summarize_spec(spec: Dict[str, Any]) -> Dict[str, Counter]:
    """
    將 CRD spec 中的 raw 列表，統計每個 node 上部屬的服務種類與數量。

    參數:
        spec: dict
            例:
            {
                "raw": [
                    {"nodeName": "node1", "serviceType": "gesture"},
                    {"nodeName": "node1", "serviceType": "gesture"},
                    {"nodeName": "node1", "serviceType": "pose"},
                ]
            }

    回傳:
        {nodeName: Counter({serviceType: 數量})}
            例:
            {
                "node1": Counter({"gesture": 2, "pose": 1})
            }
    """
    counts: Dict[str, Counter] = {}
    for item in spec.get("raw", []):
        node = item.get("nodeName")
        svc = item.get("serviceType")
        if not node or not svc:
            continue
        counts.setdefault(node, Counter())[svc] += 1
    return counts


def _signatures(counts: Dict[str, Counter]) -> Dict[str, str]:
    """
    將每個 node 的服務計數轉為穩定的簽名字串，用於比對或查表。

    參數:
        counts: {nodeName: Counter({serviceType: 數量})}
            例: {"node1": Counter({"gesture": 2, "pose": 1})}

    回傳:
        {nodeName: "node1:gesture=2,pose=1"}
    """
    sigs = {}
    for node, counter in counts.items():
        # 按服務名稱排序，確保簽名穩定
        parts = [f"{svc}={count}" for svc, count in sorted(counter.items())]
        sigs[node] = f"{node}:" + ",".join(parts)
    return sigs


def _diff_counts(old_c: Dict[str, Counter], new_c: Dict[str, Counter]) -> Dict[str, Any]:
    """
    比較舊、新兩份 node 服務計數，輸出新增/刪除/變更的差異。

    參數:
        old_c: 舊的 {nodeName: Counter}
        new_c: 新的 {nodeName: Counter}

    回傳:
        {
            "added_nodes": [...],     # 新增的 node
            "removed_nodes": [...],   # 刪除的 node
            "changed_nodes": {        # 有服務數量變動的 node
                nodeName: {
                    "added":   {svc: +數量},
                    "removed": {svc: -數量},
                    "delta":   {svc: 數量差}
                }
            }
        }
    """
    added_nodes = list(set(new_c) - set(old_c))
    removed_nodes = list(set(old_c) - set(new_c))
    changed_nodes = {}

    for node in set(old_c) & set(new_c):
        delta = Counter(new_c[node]) - Counter(old_c[node])
        removed = Counter(old_c[node]) - Counter(new_c[node])

        if delta or removed:
            changed_nodes[node] = {
                "added": dict(delta),
                "removed": dict(removed),
                "delta": {svc: new_c[node][svc] - old_c[node][svc]
                          for svc in set(new_c[node]) | set(old_c[node])}
            }

    return {
        "added_nodes": added_nodes,
        "removed_nodes": removed_nodes,
        "changed_nodes": changed_nodes,
    }


def has_deployment_changed(old_spec: Dict[str, Any], new_spec: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """
    高階方法：判斷部署環境是否變更（node 上服務部署數量變化）。

    參數:
        old_spec: 舊的 CRD spec
        new_spec: 新的 CRD spec

    回傳:
        (changed, details)
        changed: bool - 是否有變更
        details: dict - 詳細差異資訊
            {
                "old_signatures": {...},   # 舊的節點簽名
                "new_signatures": {...},   # 新的節點簽名
                "diff": {...}              # _diff_counts 的輸出
            }

    範例:
        old_spec = {"raw": [{"nodeName": "node1", "serviceType": "gesture"},
                            {"nodeName": "node1", "serviceType": "gesture"},
                            {"nodeName": "node1", "serviceType": "pose"}]}

        new_spec = {"raw": [{"nodeName": "node1", "serviceType": "gesture"},
                            {"nodeName": "node1", "serviceType": "pose"},
                            {"nodeName": "node1", "serviceType": "pose"}]}

        has_deployment_changed(old_spec, new_spec)
        =>
        (
            True,
            {
                "old_signatures": {"node1": "node1:gesture=2,pose=1"},
                "new_signatures": {"node1": "node1:gesture=1,pose=2"},
                "diff": {
                    "added_nodes": [],
                    "removed_nodes": [],
                    "changed_nodes": {
                        "node1": {
                            "added": {"pose": 1},
                            "removed": {"gesture": 1},
                            "delta": {"gesture": -1, "pose": 1}
                        }
                    }
                }
            }
        )
    """
    old_counts = _summarize_spec(old_spec)
    new_counts = _summarize_spec(new_spec)

    old_sigs = _signatures(old_counts)
    new_sigs = _signatures(new_counts)

    diff = _diff_counts(old_counts, new_counts)

    changed = bool(diff["added_nodes"] or diff["removed_nodes"] or diff["changed_nodes"])

    return changed, {
        "old_signatures": old_sigs,
        "new_signatures": new_sigs,
        "diff": diff,
    }
