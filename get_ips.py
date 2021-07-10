#!/usr/bin/env python3
import argparse
import ipaddress
from vendor_ip_ranges import get_vendor_ip_ranges
import json
import os.path

# File to save cached results to
vendor_ranges_filename = "vendor_ranges.json"

# Optional arguments
parser = argparse.ArgumentParser()
parser.add_argument('--update_ranges', action='store_true', help='Force update the ranges')
parser.add_argument('--no_minimize', action='store_true', help='Minimize the ranges into the fewest possible subnets')
parser.add_argument('--check_ip_list', default='', help='File with new line separated IPs to check')
args = parser.parse_args()


def is_in_vendor_subnet(ip_address, vendor_ranges):
    '''
    
    Given an IP address and dicts of vendor IP address ranges, identify if the IP is in any of them
    
    vendor_ranges = [{"name":"GCP", "ranges":["8.8.8.8/24".....]}, ....}]

    '''
    
    an_address = ipaddress.ip_address(ip_address)

    for vendor in vendor_ranges:
        for r in vendor['ranges']:
            a_network = ipaddress.ip_network(r)
            if an_address in a_network:
                print(f'{ip_address} is in {r}, belonging to {vendor["name"]}')
                return vendor["name"]

    return None


if __name__ == "__main__":

    # Pull the ranges if they don't exist or if you want to force upate
    if not os.path.isfile(vendor_ranges_filename) or args.update_ranges:
        f = open(vendor_ranges_filename, "w+")
        # Get all cloud vendor ranges
        vendor_ranges = get_vendor_ip_ranges(no_minimize=args.no_minimize)
        # Save the results
        f.write(json.dumps(vendor_ranges))
    else:
        f = open(vendor_ranges_filename, "r")
        vendor_ranges = json.loads(f.read().strip())

    # Check IPs against the list
    if args.check_ip_list:
        with open(args.check_ip_list, "r") as f:
            for line in f:
                if line.strip():
                    is_in_vendor_subnet(ip_address=line.strip(), vendor_ranges=vendor_ranges)  
