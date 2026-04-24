provider "iosxr" {
  host               = var.iosxr_host
  username           = var.iosxr_username
  password           = var.iosxr_password
  tls                = false
  verify_certificate = false
}
