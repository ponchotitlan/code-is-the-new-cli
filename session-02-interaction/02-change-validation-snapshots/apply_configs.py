"""Course script metadata.

Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 02 - Interaction
Module: 02 - Change Validation Snapshots
Script: apply_configs.py

Apply Loopback400 configuration to all devices in parallel using pyATS.

This script loads devices from the testbed inventory and uses pyATS pcall to
run configuration on all devices at the same time.
"""

from typing import Any

from pyats.async_ import pcall
from pyats.topology import loader

testbed = loader.load("../01-pyats-readwrite/inventory.yaml")

Loopback400_CONFIG = [
    "interface Loopback400",
    "description OOB",
    "ip address 10.220.220.223 255.255.255.255",
    "no shutdown",
]


def apply_configs(device_name: str, device: Any):
    """Apply Loopback400 configuration to one device.
    This function is executed in parallel by pyATS pcall, once per device.

    Args:
        device_name: Name of the device from the testbed inventory.
        device: pyATS device object used to connect and apply configuration.

    Raises:
        Error: Something went wrong while applying the configuration.
    """
    try:
        print(f"⚙️  Applying Loopback400 on device {device_name} ...")

        device.connect(log_stdout=False)
        device.configure(Loopback400_CONFIG)

        print(f"✅ Loopback400 configured on device {device_name}")

    except Exception as error:
        print(f"❌ Error on device {device_name}: {error}")

    finally:
        try:
            device.disconnect()  # Always disconnect, even when a device fails.
        except Exception:
            pass


# We use tuples here as stable input sequences for pcall.
names = tuple(testbed.devices.keys())
devices = tuple(testbed.devices.values())

# pcall = "parallel call" in pyATS.
pcall(apply_configs, device_name=names, device=devices)
