# cloud-vendor-ip-ranges
Get all published cloud vendor (GCP, AWS, Azure) IP ranges, save them to disk, and optional check if an IP is in one of the ranges

# Purpose
There exist times when you want to search a set of logs or IPs to see if they are from a cloud vendor, e.g. look at inbound network traffic to look for potential scanning.

To do this, you COULD lookup each IP one by one.

Instead, these scripts allow you to cache all cloud vendor IP ranges and check an IP against those ranges.

# Note/Caution
**By default, the vendor IPs are minimized to their largest whois provided CIDR, e.g. a /14 vs a /28.**

Azure has about 25,000 small (/28 and /29) IP ranges and AWS about 5,000.  While this is very specific, it can be unscalable to match an IP against one of these ranges.

By default, this script will do a whois on the ranges, get the NetRange/CIDR, and use that.  

Minimizing COULD cause FP matches, e.g. an IP from a cloud vendor office might NOT match the cloud vendor range but might show up as a match to the whois NetRange/CIDR.

You can add the --no_minimize flag if you don't want to minimize the IPs

This minimization adds about 3 minutes to the runtime.

# Methodology

vendor_ip_ranges.get_vendor_ip_ranges() compiles each vendor's IP ranges and returns a json object like below

```
[
    {"name": "Google", "ranges" : ["8.8.4.0/24", .....]},
    {"name": "AWS", "ranges" : ["13.34.37.64/27", .....]},
    {"name": "Azure", "ranges" : ["13.66.60.119/32", .....]}
]
```

These json object is then saved to vendor_ranges.json

Once the ranges are cached, you can call is_in_vendor_subnet to check if an IP is in any cloud vendor subnet.

```
Call: is_in_vendor_subnet(ip_address="35.244.160.48", vendor_ranges=vendor_ranges)
Return: Google

Call: is_in_vendor_subnet(ip_address="192.168.1.1", vendor_ranges=vendor_ranges)
Return: None

```

This will either return the vendor name (Google, AWS, Azure) if it is in one of their subnets or None if it is not.

# Recommended Application

The recommended use of this tool is to 

1. Run vendor_ip_ranges.get_vendor_ip_ranges() and save the result to a persistent location.

2. Open the saved ranges

3. Use is_in_vendor_subnet(ip_address, vendor_ranges) to lookup if the IP is in a cloud vendor's ranges

# Options

```
--no_minimize

    Do not minimize all of the subnets to their whois provided vendor NetRange/CIDR

--update 

    Force update the IP ranges even if you have a cached version

--check_ip_list

    Newline separated list of IP addresses to check
```

# Install requirements
```
pip3 install -r requirements.txt
```

# Execution
```
# Get the vendor ranges
python3 get_ips.py
```

```
# Update the vendor ranges, don't minimize them
python3 get_ips.py --update --no_minimize
```

```
# Check IPs against the vendor ranges
python3 get_ips.py --check_ip_list ip_list.txt

Example result:
35.244.160.48 is in 35.240.0.0/13, belonging to Google
2c0f:fb50:ffff:ffff:ffff:ffff:ffff:ffff is in 2c0f:fb50::/32, belonging to Google
34.232.136.167 is in 34.224.0.0/12, belonging to AWS
204.231.197.3 is in 204.231.197.0/24, belonging to Azure
```