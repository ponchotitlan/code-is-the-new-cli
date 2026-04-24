variable "iosxr_host" {
  type        = string
  description = "IP or hostname of the IOS XR device, optionally with :port (example: sandbox-iosxr-1.cisco.com:57777)"
}

variable "iosxr_username" {
  type        = string
  description = "Username for the IOS XR device"
}

variable "iosxr_password" {
  type        = string
  sensitive   = true
  description = "Password for the IOS XR device"
}

variable "demo_loopback_id" {
  type        = string
  default     = "123"
  description = "Loopback interface number, example: '123' for Loopback123"
}

variable "demo_loopback_ipv4" {
  type        = string
  default     = "10.123.123.1"
  description = "IPv4 address for the demo loopback"
}

variable "demo_loopback_mask" {
  type        = string
  default     = "255.255.255.255"
  description = "Subnet mask for the demo loopback IPv4 address"
}
