"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 03 - Models
Module: 03 - API Essentials RESTCONF
Script: restconf_connectivity_check.py
"""

import requests

# Keep output clean when verify=False is used in sandbox environments.
requests.packages.urllib3.disable_warnings()

HOST = "10.10.20.48"
PORT = 443
USERNAME = "developer"
PASSWORD = "C1sco12345"

BASE_URL = f"https://{HOST}:{PORT}/restconf/data"

response = requests.get(
    BASE_URL,
    headers={"Accept": "application/yang-data+json"},
    auth=(USERNAME, PASSWORD),
    verify=False,
    timeout=15,
    stream=True,
)

print(f"✅ Status: {response.status_code}")
response.raise_for_status()
print("🌐 RESTCONF connectivity/auth looks good!")
response.close()
