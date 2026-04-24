# Write: Create/Update a resource
#
# This actually applies changes to the target device after explicit confirmation.
# If the configuration is already there, this file does nothing.
#
# Run:  terraform apply

resource "iosxr_interface_loopback" "demo" {
  name         = var.demo_loopback_id
  description  = "CITNC_TERRAFORM_DEMO"
  shutdown     = false
  ipv4_address = var.demo_loopback_ipv4
  ipv4_netmask = var.demo_loopback_mask
}