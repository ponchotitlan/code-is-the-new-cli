"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 03 - Models
Module: 03 - API Essentials RESTCONF
Script: restconf_create_loopback.py
"""

import requests

# Keep output clean when verify=False is used in sandbox environments.
requests.packages.urllib3.disable_warnings()

HOST = "10.10.20.48"
PORT = 443
USERNAME = "developer"
PASSWORD = "C1sco12345"

BASE_URL = f"https://{HOST}:{PORT}/restconf/data"

headers = {
	"Accept": "application/yang-data+json",
	"Content-Type": "application/yang-data+json"
}

# PUT to a specific Loopback list element
resource = "Cisco-IOS-XE-native:native/interface/Loopback=300"
url = f"{BASE_URL}/{resource}"

payload = {
	"Cisco-IOS-XE-native:Loopback": {
		"name": 300,
		"description": "Telemetry",
		"ip": {
			"address": {
				"primary": {
					"address": "10.10.35.1",
					"mask": "255.255.255.255"
				}
			}
		}
	}
}

response = requests.put(
	url,
	headers=headers,
	auth=(USERNAME, PASSWORD),
	json=payload,
	verify=False,
	timeout=30,
)

print(f"Status: {response.status_code}")
if response.text:
	print(response.text)
response.raise_for_status()