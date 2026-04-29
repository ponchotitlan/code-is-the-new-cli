"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 03 - Models
Module: 02 - NETCONF Essentials
Script: netconf_commit.py
"""

import os

from dotenv import load_dotenv
from ncclient import manager

load_dotenv(".env")

HOST = os.getenv("NETCONF_HOST")
PORT = int(os.getenv("NETCONF_PORT"))
USERNAME = os.getenv("NETCONF_USERNAME")
PASSWORD = os.getenv("NETCONF_PASSWORD")

config_xml = f"""
<config>
  <interfaces xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-interface-cfg">
        <interface>
            <interface-name>Loopback300</interface-name>
            <ipv4>
                <addresses xmlns="http://cisco.com/ns/yang/Cisco-IOS-XR-um-if-ip-address-cfg">
                    <address>
                        <address>10.10.35.1</address>
                        <netmask>255.255.255.255</netmask>
                    </address>
                </addresses>
            </ipv4>
            <description>
                Telemetry
            </description>
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
    test = m.edit_config(config_xml, target='candidate', format='xml')
    print(f"✅ Edit-config response: {test}\n\n")
    
    if test.ok:
        commit = m.commit()
        print(f"✅ Commit response: {commit}\n")