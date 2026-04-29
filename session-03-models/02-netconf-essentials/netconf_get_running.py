"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 03 - Models
Module: 02 - NETCONF Essentials
Script: netconf_get_running.py
"""

import os

from dotenv import load_dotenv
from ncclient import manager

load_dotenv(".env")

HOST = os.getenv("NETCONF_HOST")
PORT = int(os.getenv("NETCONF_PORT"))
USERNAME = os.getenv("NETCONF_USERNAME")
PASSWORD = os.getenv("NETCONF_PASSWORD")

filter_xml = f"""
<interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-interface-cfg">
    <interface>
        <ipv4/>
    </interface>
</interfaces>
"""

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
    reply = m.get_config(source="running", filter=("subtree", filter_xml))
    print(reply.xml)