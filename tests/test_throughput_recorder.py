import asyncio

from event_handler.services.throughput_recorder import ThroughputRecorder


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
        recorder = ThroughputRecorder(initial_data=sample_data)
        assert await recorder.get("node1:gesture=2,pose=1", "pose") == 20
        assert await recorder.get("node1:gesture=2", "gesture") == 45
        await recorder.save("node1:gesture=2,pose=1", 55, "pose")
        assert await recorder.get("node1:gesture=2,pose=1", "pose") == 55
        # backwards compatibility with simple values
        await recorder.save("simple", 99)
        assert await recorder.get("simple") == 99

    asyncio.run(run())

