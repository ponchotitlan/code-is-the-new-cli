terraform {
  required_version = ">= 1.8.0"

  required_providers {
    iosxr = {
      source  = "CiscoDevNet/iosxr"
      version = "= 0.7.0"
    }
  }
}
