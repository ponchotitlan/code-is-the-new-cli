from pyats.topology import loader

def remediate_ntp(device) -> str:
    '''Remediate NTP configuration on a connected device.

    Args:
        device: A connected pyATS device object.

    Returns:
        The raw CLI output returned by the device after sending the configuration commands.
    '''

    cmds = [
        "ntp server 10.0.0.5 prefer",
        "ntp server 10.0.0.6",
    ]
    return device.configure(cmds)


testbed = loader.load("inventory.yaml")
r1 = testbed.devices["R1"]
r1.connect(log_stdout=False)

result = remediate_ntp(r1)
print(f"\n✅ NTP remediation result:\n{result}\n")
r1.disconnect()