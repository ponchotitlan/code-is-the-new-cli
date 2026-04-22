import json
from tqdm import tqdm
from pyats.topology import loader

# This is a list of commands we want to collect from the device.
# You can modify this list to include any commands you want to collect.
SHOW_COMMANDS = [
    "show ip interface brief",
    "show ip route summary"
]

def collect_state_parsed(device) -> dict[str, dict]:
    """Connect to a device and collect parsed outputs using Genie parsers.

    Returns:
        A dictionary with parsed structured data keyed by command.
    """
    device.connect(log_stdout=False)

    state = {}

    # We will use a special library called tqdm to show a progress bar while we collect the state.
    # This is especially useful when collecting from multiple devices or running many commands, as it gives us visual feedback on the progress of our collection.
    for cmd in tqdm(SHOW_COMMANDS, desc="Parsing commands", unit="cmd"):
        state[cmd] = device.parse(cmd) # Instead of using .execute() to get raw text output, we use .parse() to get structured data.
                                       # The rest of the logic remains the same

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
        print(f"🔖 Parsed Output:\n{json.dumps(output, indent=2)}\n") # We use a JSON parser to print these dictionaries pretty
        print(f"------")
    
    break # Remove this break to collect from all devices in the testbed
          # For the sake of this demo, we will only collect from the first device to keep the output manageable.