# Read: query an existing loopback interface from the device.
#
# This is a pure read. Terraform uses a data source to fetch current device
# state and expose it as output. No resource is created or modified.
#
# Run:  terraform plan

data "iosxr_interface_loopback" "observed" {
  name = var.demo_loopback_id
  # If the loopback does not exist yet, defer this read until apply creates it.
  depends_on = [iosxr_interface_loopback.demo]
}

output "observed_loopback_description" {
  value = data.iosxr_interface_loopback.observed.description
}

output "observed_loopback_ipv4_address" {
  value = data.iosxr_interface_loopback.observed.ipv4_address
}
