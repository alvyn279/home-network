#!/usr/bin/env python3
"""
Dynamic DNS updater for Cloudflare
Updates multiple A records when home IP changes
"""

import os
import sys
import logging
import requests
import argparse
from dotenv import load_dotenv

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
    
    def create_record(self, record_name, custom_ip=None, proxied=True):
        """Create new A record"""
        if custom_ip:
            current_ip = custom_ip
            logging.info(f"Using custom IP: {current_ip}")
        else:
            current_ip = self.get_public_ip()
            if not current_ip:
                return False
            
        # Check if record already exists
        if self.get_record_id(record_name):
            logging.info(f"Record {record_name} already exists")
            return True
            
        try:
            response = requests.post(
                f"{self.base_url}/zones/{self.zone_id}/dns_records",
                headers=self.headers,
                json={
                    "type": "A",
                    "name": record_name,
                    "content": current_ip,
                    "ttl": 300,
                    "proxied": proxied
                }
            )
            data = response.json()
            
            if data["success"]:
                proxy_status = "proxied" if proxied else "DNS only"
                logging.info(f"Created {record_name} → {current_ip} ({proxy_status})")
                return True
            else:
                logging.error(f"Failed to create {record_name}: {data}")
                return False
        except Exception as e:
            logging.error(f"Failed to create {record_name}: {e}")
            return False
    
    def update_record(self, record_name, ip, proxied=True):
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
                    "ttl": 300,
                    "proxied": proxied
                }
            )
            data = response.json()
            
            if data["success"]:
                proxy_status = "proxied" if proxied else "DNS only"
                logging.info(f"Updated {record_name} → {ip} ({proxy_status})")
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
    
    def update_all(self, records, non_proxy_records=None):
        """Update all specified records with current IP"""
        current_ip = self.get_public_ip()
        if not current_ip:
            return False
            
        # Filter out empty strings
        records = [r for r in records if r.strip()]
        non_proxy_records = [r for r in (non_proxy_records or []) if r.strip()]
        
        success_count = 0
        total_records = len(records) + len(non_proxy_records)
        
        # Update proxied records
        for record in records:
            if self.update_record(record, current_ip, proxied=True):
                success_count += 1
        
        # Update non-proxy records
        for record in non_proxy_records:
            if self.update_record(record, current_ip, proxied=False):
                success_count += 1
                
        logging.info(f"Updated {success_count}/{total_records} records")
        return success_count == total_records

def load_config():
    """Load configuration from .env file"""
    load_dotenv()
    
    return {
        "api_token": os.getenv("CLOUDFLARE_API_TOKEN"),
        "zone_id": os.getenv("CLOUDFLARE_ZONE_ID"),
        "records": os.getenv("DDNS_RECORDS", "").split(","),
        "non_proxy_records": os.getenv("DDNS_NON_PROXY_RECORDS", "").split(",")
    }

def main():
    parser = argparse.ArgumentParser(description="Dynamic DNS updater for Cloudflare")
    parser.add_argument("--init", action="store_true", 
                       help="Initialize records (create if they don't exist)")
    parser.add_argument("--add-record-once", metavar="RECORD_NAME",
                       help="Create A record (one-time)")
    parser.add_argument("--non-proxy", action="store_true",
                       help="Create record without proxy (DNS only)")
    parser.add_argument("--ip", metavar="IP_ADDRESS",
                       help="Use custom IP address instead of auto-detecting")
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
    
    # Initialize, create record once, or update DNS records
    ddns = CloudflareDDNS(config["api_token"], config["zone_id"])
    
    if args.add_record_once:
        proxied = not args.non_proxy  # Default to proxied unless --non-proxy specified
        if ddns.create_record(args.add_record_once, args.ip, proxied):
            proxy_status = "proxied" if proxied else "DNS only"
            logging.info(f"Record creation completed for {args.add_record_once} ({proxy_status})")
        else:
            logging.error(f"Record creation failed for {args.add_record_once}")
            sys.exit(1)
    elif args.init:
        if ddns.init_records(config["records"]):
            logging.info("DDNS initialization completed successfully")
        else:
            logging.error("DDNS initialization failed")
            sys.exit(1)
    else:
        if ddns.update_all(config["records"], config["non_proxy_records"]):
            logging.info("DDNS update completed successfully")
        else:
            logging.error("DDNS update failed")
            sys.exit(1)

if __name__ == "__main__":
    main()
