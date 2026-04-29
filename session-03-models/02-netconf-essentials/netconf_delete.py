"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 03 - Models
Module: 02 - NETCONF Essentials
Script: netconf_delete.py
"""

import os

from dotenv import load_dotenv
from ncclient import manager

load_dotenv(".env")

HOST = os.getenv("NETCONF_HOST")
PORT = int(os.getenv("NETCONF_PORT"))
USERNAME = os.getenv("NETCONF_USERNAME")
PASSWORD = os.getenv("NETCONF_PASSWORD")

delete_config_xml = f"""
<config>
    <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-interface-cfg">
    <interface xmlns:nc="urn:ietf:params:xml:ns:netconf:base:1.0" nc:operation="delete">
        <interface-name>Loopback300</interface-name>
    </interface>
    </interfaces>
</config>
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
    test = m.edit_config(target='candidate', config=delete_config_xml)
    print(f"✅ Delete-config response: {test}\n")
    
    if test.ok:
        commit = m.commit()
        print(f"✅ Commit response: {commit}\n")