import asyncio
from pprint import pprint
from prometheus_api_client import PrometheusConnect

PROM_URL = "http://10.52.52.111:30000"  # 視環境調整
SELECTOR = '{job="default/pose-podmonitor"}'

# --- 同步客戶端 ---
prom = PrometheusConnect(url=PROM_URL, disable_ssl=True)

# --- 封裝成可在 async 內呼叫的 helper ---
async def q(query: str):
    # prometheus-api-client 是同步的，用 thread 不阻塞事件迴圈
    return await asyncio.to_thread(prom.custom_query, query)

async def main():
    # 1) target 是否 UP
    print(f"[querying {PROM_URL} for {SELECTOR}]")
    res_up = await q(f"up{SELECTOR}")
    print("\n[UP]")
    pprint(res_up)

    # 2) 探索有哪些 metric：列出 metric 名稱與序列數
    #   等同於 count by(__name__) ( {...} )
    res_names = await q(f"count by(__name__) ({SELECTOR})")
    print("\n[metric names under this target]")
    names = []
    for s in res_names:
        # prometheus-api-client 回傳 list[dict]，每個元素含 metric/value
        m = s.get("metric", {}).get("__name__")
        v = s.get("value", [None, None])[1]
        if m:
            names.append(m)
            print(f"{m}: {v}")

    # 3) 篩 throughput 相關的 metric 名稱
    thr_names = [n for n in names if "throughput" in n]
    print("\n[candidate throughput metrics]")
    print(thr_names or "(none)")

    # 4) 逐個查詢 throughput metric 的當前值
    for m in thr_names:
        qstr = f"{m}{SELECTOR}"
        res = await q(qstr)
        print(f"\n[{qstr}]")
        if not res:
            print("(no data)")
            continue
        for i, series in enumerate(res, 1):
            ts, val = series.get("value", [None, None])
            print(f"{i}. value={val} @ {ts} labels={series.get('metric', {})}")

if __name__ == "__main__":
    asyncio.run(main())
