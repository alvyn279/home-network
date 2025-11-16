#!/usr/bin/env python3
"""
Internet Monitor - Automatic Modem Reset via Smart Plug
Monitors internet connectivity and power cycles modem when failures detected.
"""

import os
import asyncio
import subprocess
import logging
import random
from kasa import Discover

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('internet-monitor')

class InternetMonitor:
    def __init__(self):
        # Load configuration from environment variables
        self.plug_ip = os.getenv('PLUG_IP')
        self.check_interval_in_seconds = int(os.getenv('CHECK_INTERVAL_IN_SECONDS'))
        self.failure_threshold = int(os.getenv('FAILURE_THRESHOLD'))
        self.test_hosts = os.getenv('TEST_HOSTS').split(',')
        self.restart_delay_in_seconds = int(os.getenv('RESTART_DELAY_IN_SECONDS'))
        self.recovery_wait_in_seconds = int(os.getenv('RECOVERY_WAIT_IN_SECONDS'))
        
        logger.info("Internet Monitor Starting:")
        logger.info(f"  Smart Plug: {self.plug_ip}")
        logger.info(f"  Check Interval: {self.check_interval_in_seconds}s")
        logger.info(f"  Failure Threshold: {self.failure_threshold}")
        logger.info(f"  Test Hosts: {', '.join(self.test_hosts)}")
        
    def ping_test(self, host):
        """Test connectivity to a single host"""
        try:
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', host], 
                capture_output=True, 
                timeout=5
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            logger.error(f"Ping error to {host}: {e}")
            return False
    
    def check_internet(self):
        """Test internet connectivity using multiple hosts"""
        # Randomize test order for better load distribution
        hosts = self.test_hosts.copy()
        random.shuffle(hosts)
        
        for host in hosts:
            if self.ping_test(host):
                return True
        return False
    
    async def restart_modem(self):
        """Power cycle the modem via smart plug"""
        try:
            # Use new API instead of deprecated SmartPlug
            device = await Discover.discover_single(self.plug_ip)
            
            logger.warning("Restarting modem...")
            
            # Turn off modem
            await device.turn_off()
            logger.info("Modem powered OFF")
            await asyncio.sleep(self.restart_delay_in_seconds)
            
            # Turn on modem
            await device.turn_on()
            logger.info("Modem powered ON")
            logger.info(f"Waiting {self.recovery_wait_in_seconds}s for modem recovery...")
            
        except Exception as e:
            logger.error(f"Failed to restart modem: {e}")
            raise
    
    async def monitor(self):
        """Main monitoring loop"""
        failures = 0
        
        logger.info("Monitoring started")
        
        while True:
            try:
                if self.check_internet():
                    if failures > 0:
                        logger.info(f"Internet restored after {failures} failures")
                    failures = 0
                else:
                    failures += 1
                    logger.warning(f"Internet down ({failures}/{self.failure_threshold})")
                    
                    if failures >= self.failure_threshold:
                        logger.warning("Triggering modem restart")
                        await self.restart_modem()
                        failures = 0
                        # Wait longer after restart for modem to fully recover
                        await asyncio.sleep(self.recovery_wait_in_seconds)
                        continue
                
                # Normal check interval
                await asyncio.sleep(self.check_interval_in_seconds)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                # Wait a bit before retrying to avoid rapid failures
                await asyncio.sleep(30)

def main():
    """Entry point"""
    monitor = InternetMonitor()
    try:
        asyncio.run(monitor.monitor())
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()
