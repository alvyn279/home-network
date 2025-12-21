#!/usr/bin/env python3
"""
Internet Monitor - Automatic Modem Reset via Smart Plug
Monitors internet connectivity and power cycles modem when failures detected.
"""

import os
import sys
import asyncio
import subprocess
import logging
import random
import time
import argparse
from datetime import datetime

from kasa import Discover
from dotenv import load_dotenv
from prometheus_client import Counter, start_http_server

# Configure logging (will be updated based on test mode in constructor)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('internet-monitor')

class InternetMonitor:
    def __init__(self, test_mode=False, metrics_enabled=False):
        self.test_mode = test_mode
        self.metrics_enabled = metrics_enabled
        
        # Set logging level based on test mode
        if self.test_mode:
            logging.getLogger().setLevel(logging.DEBUG)
        
        # Load test environment if in test mode
        if self.test_mode:
            load_dotenv('test.env')
            print("Loaded test configuration from test.env")
        
        # Initialize Prometheus metrics if enabled
        if self.metrics_enabled:
            self.ping_success_counter = Counter('ping_success_total', 'Successful ping attempts', ['host'])
            self.ping_failure_counter = Counter('ping_failure_total', 'Failed ping attempts', ['host'])
            self.internet_up_counter = Counter('internet_up_total', 'Internet connectivity checks that passed')
            self.internet_down_counter = Counter('internet_down_total', 'Internet connectivity checks that failed')
            self.modem_restart_counter = Counter('modem_restart_total', 'Number of modem restarts triggered')
        else:
            self.ping_success_counter = None
            self.ping_failure_counter = None
            self.internet_up_counter = None
            self.internet_down_counter = None
            self.modem_restart_counter = None
        
        # Load configuration from environment variables
        self.plug_ip = os.getenv('PLUG_IP')
        self.check_interval_in_seconds = int(os.getenv('CHECK_INTERVAL_IN_SECONDS'))
        self.failure_threshold = int(os.getenv('FAILURE_THRESHOLD'))
        self.test_hosts = os.getenv('TEST_HOSTS').split(',')
        self.restart_delay_in_seconds = int(os.getenv('RESTART_DELAY_IN_SECONDS'))
        self.recovery_wait_in_seconds = int(os.getenv('RECOVERY_WAIT_IN_SECONDS'))
        
        # Stats tracking for production
        self.stats = {host: {'success': 0, 'total': 0} for host in self.test_hosts}
        self.last_stats_report = time.time()
        
        # Outage simulation for test mode only
        if self.test_mode:
            self.simulate_outage = os.getenv('SIMULATE_OUTAGE', 'false').lower() == 'true'
            self.start_time = time.time()
            self.outage_trigger_time = None
            self.outage_recovery_time = None
            self.outage_active = False
            self.outage_completed = False
            
            if self.simulate_outage:
                # Random outage between 30-60 seconds after start
                self.outage_trigger_time = self.start_time + random.randint(30, 60)
                logger.info(f"Outage simulation enabled - will trigger at {int(self.outage_trigger_time - self.start_time)}s")
        
        logger.info("Internet Monitor Starting:")
        logger.info(f"  Smart Plug: {self.plug_ip}")
        logger.info(f"  Check Interval: {self.check_interval_in_seconds}s")
        logger.info(f"  Failure Threshold: {self.failure_threshold}")
        logger.info(f"  Test Hosts: {', '.join(self.test_hosts)}")
        
    def ping_test(self, host):
        """Test connectivity to a single host"""
        # Outage simulation (test mode only)
        if self.test_mode:
            current_time = time.time()
            
            # Check if we should trigger outage simulation (only once)
            if (self.simulate_outage and not self.outage_active and not self.outage_completed 
                and current_time >= self.outage_trigger_time):
                self.outage_active = True
                # Set recovery time 60-90 seconds after outage starts
                self.outage_recovery_time = current_time + random.randint(60, 90)
                recovery_duration = int(self.outage_recovery_time - current_time)
                logger.warning(f"🔥 SIMULATED OUTAGE TRIGGERED - Will recover in {recovery_duration}s")
            
            # Check if we should recover from outage
            if self.outage_active and current_time >= self.outage_recovery_time:
                self.outage_active = False
                self.outage_completed = True
                logger.warning("✅ SIMULATED OUTAGE RECOVERED - Pings will now succeed")
            
            # If outage is active, simulate failure
            if self.outage_active:
                logger.debug(f"✗ {host} failed (simulated outage)")
                return False
        
        success = False
        try:
            if self.test_mode:
                logger.debug(f"Pinging {host}...")
            
            result = subprocess.run(
                ['ping', '-c', '1', '-W', '3', host], 
                capture_output=True, 
                timeout=5,
                text=True
            )
            
            success = result.returncode == 0
            
            if self.test_mode:
                if success:
                    # Extract ping time from output
                    output_lines = result.stdout.strip().split('\n')
                    ping_line = next((line for line in output_lines if 'time=' in line), '')
                    if ping_line:
                        time_part = ping_line.split('time=')[1].split()[0]
                        logger.debug(f"✓ {host} responded in {time_part}")
                    else:
                        logger.debug(f"✓ {host} responded (no timing info)")
                else:
                    logger.debug(f"✗ {host} failed (exit code: {result.returncode})")
            
        except subprocess.TimeoutExpired:
            if self.test_mode:
                logger.debug(f"✗ {host} timed out (>5s)")
            success = False
        except Exception as e:
            logger.error(f"Ping error to {host}: {e}")
            success = False
        
        # Update logged stats
        if not self.test_mode:
            self.stats[host]['total'] += 1
            if success:
                self.stats[host]['success'] += 1
            
            # Report hourly stats
            current_time = time.time()
            if current_time - self.last_stats_report >= 3600:  # 1 hour
                self.report_hourly_stats()
                self.last_stats_report = current_time
        
        # Update Prometheus metrics (if enabled)
        if self.metrics_enabled:
            if success:
                self.ping_success_counter.labels(host=host).inc()
            else:
                self.ping_failure_counter.labels(host=host).inc()
        
        return success
    
    def report_hourly_stats(self):
        """Report ping success statistics for the past hour"""
        current_hour = datetime.now().strftime("%Y-%m-%d %H:00")
        logger.info(f"📊 Hourly Ping Statistics ({current_hour}):")
        for host in self.test_hosts:
            stats = self.stats[host]
            if stats['total'] > 0:
                success_rate = (stats['success'] / stats['total']) * 100
                logger.info(f"  {host}: {stats['success']}/{stats['total']} ({success_rate:.1f}%)")
            else:
                logger.info(f"  {host}: No pings recorded")
        
        # Reset stats for next hour
        self.stats = {host: {'success': 0, 'total': 0} for host in self.test_hosts}
    
    def check_internet(self):
        """Test internet connectivity using multiple hosts"""
        internet_available = False
        
        # Ping all hosts to get complete metrics
        for host in self.test_hosts:
            if self.ping_test(host):
                internet_available = True
        
        # Update internet connectivity metrics (if enabled)
        if self.metrics_enabled:
            if internet_available:
                self.internet_up_counter.inc()
            else:
                self.internet_down_counter.inc()
        
        return internet_available
    
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
            
            # Update modem restart metrics (if enabled)
            if self.metrics_enabled:
                self.modem_restart_counter.inc()
            
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
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Internet Monitor - Automatic Modem Reset")
    parser.add_argument("--test", action="store_true", 
                       help="Run in test mode with test.env configuration")
    parser.add_argument("--with-metrics", action="store_true",
                       help="Enable Prometheus metrics server")
    parser.add_argument("--metrics-port", type=int, default=8000,
                       help="Port for Prometheus metrics server (default: 8000)")
    args = parser.parse_args()
    
    # Start Prometheus metrics server if enabled
    if args.with_metrics:
        try:
            start_http_server(args.metrics_port)
            logger.info(f"📊 Prometheus metrics server started on port {args.metrics_port}")
            logger.info(f"   Metrics available at http://localhost:{args.metrics_port}/metrics")
        except Exception as e:
            logger.error(f"Failed to start metrics server on port {args.metrics_port}: {e}")
            sys.exit(1)
    
    monitor = InternetMonitor(test_mode=args.test, metrics_enabled=args.with_metrics)
    try:
        asyncio.run(monitor.monitor())
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()
