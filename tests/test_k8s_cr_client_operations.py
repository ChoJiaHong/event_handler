import asyncio
from infra.k8s_cr_client import K8sCustomResourceClient


def test_k8s_cr_client_operations():
    async def run():
        client = K8sCustomResourceClient()
        service_info = await client.get_service_info()
        assert service_info in (None, {})
        subscription_info = await client.get_subscription_info()
        assert subscription_info in (None, {})
        services = await client.list_custom_resources(
            "ha.example.com", "v1", "default", "services"
        )
        assert isinstance(services, list)

    asyncio.run(run())

