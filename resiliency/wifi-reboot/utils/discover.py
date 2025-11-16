import asyncio
from kasa import Discover

HOME_NETWORK_DISCOVERY_IP = "192.168.0.255"

async def main():
    devices = await Discover.discover(
        target=HOME_NETWORK_DISCOVERY_IP,
        username="REDACTED_FOR_SECURITY",
        password="REDACTED_FOR_SECURITY",
    )
    print([dev.model for dev in devices.values()])
    
if __name__ == "__main__":
    asyncio.run(main())


