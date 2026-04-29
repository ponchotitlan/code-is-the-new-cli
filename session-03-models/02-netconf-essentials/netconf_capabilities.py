"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 03 - Models
Module: 02 - NETCONF Essentials
Script: netconf_capabilities.py
"""

import os
from dotenv import load_dotenv
from ncclient import manager

load_dotenv(".env")

HOST = os.getenv("NETCONF_HOST")
PORT = int(os.getenv("NETCONF_PORT"))
USERNAME = os.getenv("NETCONF_USERNAME")
PASSWORD = os.getenv("NETCONF_PASSWORD")

with manager.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    hostkey_verify=False,
    allow_agent=False,
    look_for_keys=False,
    timeout=30,
) as m:
    print(f"✅ Connected! Session ID: {m.session_id}")
    print("🙌🏽 Server capabilities (a looong list):")
    for capability in m.server_capabilities:
        print(f"- {capability}")