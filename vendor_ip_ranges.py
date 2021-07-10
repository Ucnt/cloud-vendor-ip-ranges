#!/usr/bin/env python3
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import json
import re
from ipwhois import IPWhois
import ipaddress
from tqdm import tqdm


def get_minimum_set_ranges(ranges):
    '''
        Purpose: For a given array of IP ranges, go through them to get the minimum set

        Reason: Some vendors give a large number of small /28 and /29 CIDRs instead of the main /14 or /16.  
        So you have THOUSANDS of ranges instead of a few dozen or hundred.

        Method:
            For every range, see if it exists as a range or sub-range in the final_list of ranges
                if not, lookup whois for the range and get the ranges from it:
                    add whois ranges to final_list
    '''
    print("Getting minimal set of ranges...this may take some time...")
    final_ranges = []
    for r in tqdm(ranges):
        # Just in case there is an issue doing whois, just add the range
        try:
            ip = r.split('/')[0]
            
            ip_address = ipaddress.ip_address(ip)
            for final_r in final_ranges:
                if ip_address in ipaddress.ip_network(final_r):
                    break
            else:
                obj = IPWhois(ip)
                try:
                    final_ranges.extend(obj.lookup_whois(asn_methods=['dns', 'whois', 'http'])['nets'][0]['cidr'].split(", "))
                except:
                    if final_ranges.append(obj.lookup_whois(asn_methods=['dns', 'whois', 'http'])['asn_cidr']) == "NA":
                        final_ranges.append(r)
                    else:
                        final_ranges.append(obj.lookup_whois(asn_methods=['dns', 'whois', 'http'])['asn_cidr'])
        except Exception as e:
            final_ranges.append(r)

        final_ranges = list(set(final_ranges))

    return final_ranges


def get_azure_ranges(no_minimize):
    r = requests.get("https://www.microsoft.com/en-us/download/confirmation.aspx?id=56519", verify=False)
    download_link = re.findall(r"https:\/\/download.microsoft.com\/download\/[a-zA-Z0-9\/_\.\-]+", r.text)
    ranges = []
    if download_link:
        r2 = requests.get(download_link[0], verify=False)
        r2_json = json.loads(r2.text.strip())

        for value in r2_json['values']:
            for item in value['properties']['addressPrefixes']:
                ranges.append(item)

    # Get the set of ranges (there will be duplicates)
    ranges = list(set(ranges))

    if no_minimize:
        return ranges
    else:
        # Get the minimal set of ranges that are necessary
        ranges = get_minimum_set_ranges(ranges)
        return


def get_google_ranges(no_minimize):
    r = requests.get("https://www.gstatic.com/ipranges/goog.json", verify=False)
    r_json = json.loads(r.text.strip())
    
    ranges = []

    for prefix in r_json['prefixes']:
        try:
            ranges.append(prefix['ipv4Prefix'])
        except:
            try:
                ranges.append(prefix['ipv6Prefix'])
            except:
                pass

    # Get the set of ranges (there will be duplicates)
    ranges = list(set(ranges))

    if no_minimize:
        return ranges
    else:
        # Get the minimal set of ranges that are necessary
        ranges = get_minimum_set_ranges(ranges)
        return


def get_aws_ranges(no_minimize):
    r = requests.get("https://ip-ranges.amazonaws.com/ip-ranges.json", verify=False)
    r_json = json.loads(r.text.strip())

    ranges = []
    
    for prefix in r_json['prefixes']:
        try:
            ranges.append(prefix['ip_prefix'])
        except:
            pass

    for prefix in r_json['ipv6_prefixes']:
        try:
            ranges.append(prefix['ipv6_prefix'])
        except:
            pass

    # Get the set of ranges (there will be duplicates)
    ranges = list(set(ranges))

    if no_minimize:
        return ranges
    else:
        # Get the minimal set of ranges that are necessary
        ranges = get_minimum_set_ranges(ranges)
        return


def get_vendor_ip_ranges(no_minimize):
    ranges = []

    # Get Azure ranges
    print("Getting Azure ranges")
    azure_ranges = get_azure_ranges(no_minimize=no_minimize)
    ranges.append({"name":"Azure", "ranges": azure_ranges})
    print(f"Got {len(azure_ranges)} Azure ranges")
    
    # Get Google Ranges
    print("Getting Google ranges")
    google_ranges = get_google_ranges(no_minimize=no_minimize)
    ranges.append({"name":"Google", "ranges": google_ranges})
    print(f"Got {len(google_ranges)} Google ranges")

    # Get AWS ranges
    print("Getting AWS ranges")
    aws_ranges = get_aws_ranges(no_minimize=no_minimize)
    ranges.append({"name":"AWS", "ranges": aws_ranges})
    print(f"Got {len(aws_ranges)} AWS ranges")

    # Return all ranges
    return ranges