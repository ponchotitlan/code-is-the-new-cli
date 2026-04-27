"""Course script metadata.

Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 02 - Interaction
Module: 01 - pyATS Read and Write
Script: state_collector_remediator.py
"""

import json
from tqdm import tqdm
from pyats.topology import loader

# This is a list of commands we want to collect from the device.
# You can modify this list to include any commands you want to collect.
SHOW_COMMANDS = [
    "show ip interface brief"
]

LOOPBACK100_REMEDIATION_COMMANDS = [
    "interface Loopback100",
    "ip address 10.100.100.103 255.255.255.255",
    "no shutdown",
]

def collect_state_parsed(device) -> dict[str, dict]:
    """Collect parsed outputs from a connected device using Genie parsers.

    Returns:
        A dictionary with parsed structured data keyed by command.
    """
    state = {}

    for cmd in tqdm(SHOW_COMMANDS, desc="Parsing commands", unit="cmd"):
        state[cmd] = device.parse(cmd)

    return state


def detect_loopback_drift(device: "pyats.devices.Device") -> bool:
    """Detect drift in Loopback100 interface configuration.

    Args:
        device: A connected pyATS device object.

    Returns:
        True if Loopback100 is missing or any of its features don't match the expected configuration, False otherwise.
    """
    parsed_interfaces = collect_state_parsed(device)["show ip interface brief"]     # We get the parsed output of the "show ip interface brief" command,
                                                                                    # which is a dictionary containing an "interface" key with details about all interfaces on the device.
    interface_table = parsed_interfaces.get("interface", {})                        # The get() method is used to safely access the "interface" key, returning an empty dictionary if it doesn't exist.
                                                                                    # This prevents potential KeyError exceptions if the command output doesn't include the expected structure.
                                                                                    
    print(f"🔍 Checking for Loopback100 in the interface table: \n{json.dumps(interface_table, indent=2)}\n") # We print the interface table to see what interfaces are currently present on the device.

    # Check if Loopback100 exists
    if "Loopback100" not in interface_table:
        return True
    
    loopback_config = interface_table["Loopback100"]
    
    # Check if the IP address matches
    if loopback_config.get("ip_address") != "10.100.100.103":
        return True
    
    return False


def remediate_loopback(device: "pyats.devices.Device") -> str:
    """Apply the Loopback100 remediation commands to the connected device.

    Args:
        device: A connected pyATS device object.

    Returns:
        The raw CLI output returned by the device after sending the configuration commands.
    """
    return device.configure(LOOPBACK100_REMEDIATION_COMMANDS)


testbed = loader.load("inventory.yaml")

for name, device in testbed.devices.items():
    
    print(f"\n🔍 Collecting state from {name}")
    print(f"Device details: {device}\n\n")
    device.connect(log_stdout=False)
    
    drift_detected = detect_loopback_drift(device)

    print("------")
    if drift_detected:
        print("⚠️ Drift detected: Loopback100 is missing or doesn't have IP 10.100.100.103. Applying remediation...\n")
        remediation_result = remediate_loopback(device)
        print(f"✅ Remediation result:\n{remediation_result}\n")
    else:
        print("✅ No drift detected: Loopback100 is present and correctly configured.\n")
    
    break # Remove this break to collect from all devices in the testbed
          # For the sake of this demo, we will only collect from the first device to keep the output manageable.