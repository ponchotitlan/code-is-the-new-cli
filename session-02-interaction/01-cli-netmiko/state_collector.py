from pyats.topology import loader

# This is a list of commands we want to collect from the device.
# You can modify this list to include any commands you want to collect.
SHOW_COMMANDS = [
    "show ip interface brief",
    "show ip route summary"
]

def collect_state(device) -> dict[str, dict]:
    """Connect to a device and collect raw outputs.

    Returns:
        A dictionary with raw sections keyed by command.
    """
    device.connect(log_stdout=True)  # Connect to the device and log the connection process.
                                     # The logging is optional, but we want to see the connection process in the output for this demo.

    state = {}  # This is an empty dictionary where we will store the results of our commands.

    for cmd in SHOW_COMMANDS:
        state[cmd] = device.execute(cmd) # The key is the command, and the value is the raw output of the command.
                                         # This will look like: state["show ip interface brief"] = "raw output of the command"

    return state


testbed = loader.load("inventory.yaml")

for name, device in testbed.devices.items():
    # When we loop over the .items() of the devices, we get both the name and the device object.
    # This is useful for printing the name of the device along with the collected state.
    
    print(f"\n🔍 Collecting state from {name}")
    print(f"Device details: {device}\n\n")
    
    state = collect_state(device)
    
    # Let's print the raw results of the commands, one by one
    print(f"------")
    for cmd, output in state.items():
        print(f"\n🔑 Command: {cmd}\n\n")
        print(f"🔖 Output:\n{output}\n")
        print(f"------")
    
    break # Remove this break to collect from all devices in the testbed
          # For the sake of this demo, we will only collect from the first device to keep the output manageable.