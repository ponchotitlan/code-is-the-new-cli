"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 02 - Interaction
Module: 01 - pyATS Read and Write
Script: state_collector_parse_handle.py
"""

import json
from tqdm import tqdm
from pyats.topology import loader
from genie.libs.parser.utils.common import ParserNotFound

SHOW_COMMANDS = [
    "show ip interface brief | exclude unassigned"
]

def collect_state_parsed(device) -> dict[str, dict | str]:
    """Connect to a device and collect parsed outputs using Genie parsers.

    Returns:
        A dictionary keyed by command. Values are parsed structured data when
        a Genie parser is available, or raw CLI output when no parser exists.

    Raises:
        ParserNotFound: Raised by ``device.parse`` when a parser is not
            available for a command. This exception is handled internally and
            the function falls back to raw CLI output for that command.
    """
    device.connect(log_stdout=False)

    state = {}
    for cmd in tqdm(SHOW_COMMANDS, desc="Parsing commands", unit="cmd"):
        try:
            state[cmd] = device.parse(cmd)
        except ParserNotFound as error:                         # If the parser is not found for a command, we catch the ParserNotFound exception
                                                                # and print a warning message. We then fall back to using device.execute(cmd) to get
                                                                # the raw CLI output for that command, which we store in the state dictionary.
            print(f"🚨 Parser not found for '{cmd}': {error}")
            state[cmd] = device.execute(cmd)

    return state


testbed = loader.load("inventory.yaml")

for name, device in testbed.devices.items():
    # When we loop over the .items() of the devices, we get both the name and the device object.
    # This is useful for printing the name of the device along with the collected state.
    
    print(f"\n🔍 Collecting state from {name}")
    print(f"Device details: {device}\n\n")
    
    state = collect_state_parsed(device)
    
    # Let's print the parsed results of the commands, one by one
    print(f"------")
    for cmd, output in state.items():
        print(f"\n🔑 Command: {cmd}\n\n")
        print(f"🔖 Output:\n{json.dumps(output, indent=2)}\n") # We use a JSON parser to print these dictionaries pretty
        print(f"------")
    
    break # Remove this break to collect from all devices in the testbed
          # For the sake of this demo, we will only collect from the first device to keep the output manageable.