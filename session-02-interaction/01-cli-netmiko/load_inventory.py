from pyats.topology import loader


if __name__ == "__main__":
    testbed = loader.load("inventory.yaml")

    for device_name, device in testbed.devices.items():
        print(f"{device_name}: os={device.os}, type={device.type}")