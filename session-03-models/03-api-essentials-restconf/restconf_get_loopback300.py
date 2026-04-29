"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 03 - Models
Module: 03 - API Essentials RESTCONF
Script: restconf_get_loopback300.py
"""

import json
import requests

# Keep output clean when verify=False is used in sandbox environments.
requests.packages.urllib3.disable_warnings()

HOST = "10.10.20.48"
PORT = 443
USERNAME = "developer"
PASSWORD = "C1sco12345"

BASE_URL = f"https://{HOST}:{PORT}/restconf/data"

headers = {
	"Accept": "application/yang-data+json"
}

resource = "Cisco-IOS-XE-native:native/interface/Loopback=300"
url = f"{BASE_URL}/{resource}"

response = requests.get(
	url,
	headers=headers,
	auth=(USERNAME, PASSWORD),
	verify=False,
	timeout=30,
)

print(f"Status: {response.status_code}")
print(json.dumps(response.json(), indent=2))