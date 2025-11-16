import asyncio
from kasa import Discover

async def test_control():
    print("Testing with new API...")
    
    # Use new API
    device = await Discover.discover_single("192.168.0.38")
    await device.update()
    
    print(f"Device: {device.alias} ({device.model})")
    print(f"Currently: {'ON' if device.is_on else 'OFF'}")
    
    # Test control
    print("Turning OFF...")
    await device.turn_off()
    await asyncio.sleep(2)
    
    print("Turning ON...")
    await device.turn_on()
    
    print("Control test complete!")

if __name__ == "__main__":
    asyncio.run(test_control())

