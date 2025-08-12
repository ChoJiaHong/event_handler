import asyncio

from infrastructure.throughput_repository import JSONThroughputRepository

sample_data = {
    "node1:gesture=2,pose=1": {
        "pose": {"throughput": 20},
        "gesture": {"throughput": 30},
    },
    "node1:gesture=1,pose=2": {
        "pose": {"throughput": 35},
        "gesture": {"throughput": 20},
    },
    "node1:pose=1": {"pose": {"throughput": 50}},
    "node1:gesture=2": {"gesture": {"throughput": 45}},
    "node1:gesture=2,pose=2": {
        "pose": {"throughput": 25},
        "gesture": {"throughput": 25},
    },
    "node2:object=1,pose=1": {
        "pose": {"throughput": 40},
        "object": {"throughput": 15},
    },
    "node2:gesture=2": {"gesture": {"throughput": 38}},
    "node1:pose=3": {"pose": {"throughput": 18}},
}


def test_throughput_recorder_nested():
    async def run():
        recorder = JSONThroughputRepository(initial_data=sample_data)
        key = {"node": "node1", "services": {"gesture": 2, "pose": 1}}
        assert await recorder.get(key, "pose") == 20
        assert await recorder.get({"node": "node1", "services": {"gesture": 2}}, "gesture") == 45
        await recorder.save(key, 55, "pose")
        assert await recorder.get(key, "pose") == 55
        await recorder.save({"node": "simple", "services": {}}, 99)
        assert await recorder.get({"node": "simple", "services": {}}) == 99

    asyncio.run(run())


def test_throughput_recorder_key_normalization():
    async def run():
        recorder = JSONThroughputRepository(initial_data=sample_data)
        key_rev = {"node": "node1", "services": {"pose": 1, "gesture": 2}}
        assert await recorder.get(key_rev, "gesture") == 30
        await recorder.save(key_rev, 99, "pose")
        key_norm = {"node": "node1", "services": {"gesture": 2, "pose": 1}}
        assert await recorder.get(key_norm, "pose") == 99

    asyncio.run(run())
