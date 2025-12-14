#!/usr/bin/env python3
"""
Dynamic DNS updater for Cloudflare
Updates multiple A records when home IP changes
"""

import os
import sys
import json
import logging
import requests
import argparse
from datetime import datetime

class CloudflareDDNS:
    def __init__(self, api_token, zone_id):
        self.api_token = api_token
        self.zone_id = zone_id
        self.base_url = "https://api.cloudflare.com/client/v4"
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }
        
    def get_public_ip(self):
        """Get current public IP address"""
        try:
            response = requests.get("https://ipv4.icanhazip.com", timeout=10)
            return response.text.strip()
        except Exception as e:
            logging.error(f"Failed to get public IP: {e}")
            return None
    
    def get_record_id(self, record_name):
        """Get DNS record ID for given name"""
        try:
            response = requests.get(
                f"{self.base_url}/zones/{self.zone_id}/dns_records",
                headers=self.headers,
                params={"name": record_name, "type": "A"}
            )
            data = response.json()
            
            if data["success"] and data["result"]:
                return data["result"][0]["id"]
            return None
        except Exception as e:
            logging.error(f"Failed to get record ID for {record_name}: {e}")
            return None
    
    def create_record(self, record_name, ip):
        """Create new A record"""
        try:
            response = requests.post(
                f"{self.base_url}/zones/{self.zone_id}/dns_records",
                headers=self.headers,
                json={
                    "type": "A",
                    "name": record_name,
                    "content": ip,
                    "ttl": 300,
                    "proxied": True
                }
            )
            data = response.json()
            
            if data["success"]:
                logging.info(f"Created {record_name} → {ip}")
                return True
            else:
                logging.error(f"Failed to create {record_name}: {data}")
                return False
        except Exception as e:
            logging.error(f"Failed to create {record_name}: {e}")
            return False
    
    def update_record(self, record_name, ip):
        """Update A record with new IP"""
        record_id = self.get_record_id(record_name)
        if not record_id:
            logging.error(f"Record not found: {record_name}")
            return False
            
        try:
            response = requests.put(
                f"{self.base_url}/zones/{self.zone_id}/dns_records/{record_id}",
                headers=self.headers,
                json={
                    "type": "A",
                    "name": record_name,
                    "content": ip,
                    "ttl": 300
                }
            )
            data = response.json()
            
            if data["success"]:
                logging.info(f"Updated {record_name} → {ip}")
                return True
            else:
                logging.error(f"Failed to update {record_name}: {data}")
                return False
        except Exception as e:
            logging.error(f"Failed to update {record_name}: {e}")
            return False
    
    def init_records(self, records):
        """Initialize records - create if they don't exist"""
        current_ip = self.get_public_ip()
        if not current_ip:
            return False
            
        success_count = 0
        for record in records:
            if self.get_record_id(record):
                logging.info(f"Record {record} already exists")
                success_count += 1
            else:
                if self.create_record(record, current_ip):
                    success_count += 1
                    
        logging.info(f"Initialized {success_count}/{len(records)} records")
        return success_count == len(records)
    
    def update_all(self, records):
        """Update all specified records with current IP"""
        current_ip = self.get_public_ip()
        if not current_ip:
            return False
            
        success_count = 0
        for record in records:
            if self.update_record(record, current_ip):
                success_count += 1
                
        logging.info(f"Updated {success_count}/{len(records)} records")
        return success_count == len(records)

def load_config():
    """Load configuration from environment or config file"""
    config_file = os.path.join(os.path.dirname(__file__), "config.json")
    
    # Try config file first
    if os.path.exists(config_file):
        with open(config_file) as f:
            return json.load(f)
    
    # Fall back to environment variables
    return {
        "api_token": os.getenv("CLOUDFLARE_API_TOKEN"),
        "zone_id": os.getenv("CLOUDFLARE_ZONE_ID"),
        "records": os.getenv("DDNS_RECORDS", "").split(",")
    }

def main():
    parser = argparse.ArgumentParser(description="Dynamic DNS updater for Cloudflare")
    parser.add_argument("--init", action="store_true", 
                       help="Initialize records (create if they don't exist)")
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = load_config()
    
    if not config["api_token"] or not config["zone_id"]:
        logging.error("Missing API token or zone ID")
        sys.exit(1)
    
    if not config["records"] or config["records"] == [""]:
        logging.error("No records specified")
        sys.exit(1)
    
    # Initialize or update DNS records
    ddns = CloudflareDDNS(config["api_token"], config["zone_id"])
    
    if args.init:
        if ddns.init_records(config["records"]):
            logging.info("DDNS initialization completed successfully")
        else:
            logging.error("DDNS initialization failed")
            sys.exit(1)
    else:
        if ddns.update_all(config["records"]):
            logging.info("DDNS update completed successfully")
        else:
            logging.error("DDNS update failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
