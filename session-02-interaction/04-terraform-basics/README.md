# 🌐 Session 04 (Extra): OpenTofu Basics with IOS XR
Topics: 🧱 OpenTofu state · ⚖️ Paradigm shift vs Ansible · 🌐 Cisco IOS XR provider

---

## 🎯 By the end of this lesson you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 🧱 Explain what OpenTofu is and why state is central to its workflow |
| 2 | ⚖️ Compare Ansible task-declarative automation with OpenTofu state-driven imperativeness |
| 3 | 📖 Read interface data from IOS XR using the official Cisco OpenTofu/Terraform provider |
| 4 | ✍️ Create a loopback interface declaratively and validate convergence |
| 5 | 🧹 Remove the loopback cleanly through Terraform lifecycle operations |

---

## 🗺️ What is going on

<div align="center"><img src="../../images/citnc_banner_08.png" width="80%"/></div></br>

---

In the Ansible lesson, we modeled interface **intent** through tasks and modules. In this extra lesson, we keep the same interface lifecycle examples (read, create, delete) but switch to `OpenTofu` with the official Cisco IOS XR provider.

**🏅 Golden rule No.4:**
> In OpenTofu, your source of truth is not only the code, but code + state.

---

## ⬜️ The tastiest tofu in town

OpenTofu is an open-source tool that lets you describe your infrastructure in code files, and then automatically figures out what changes need to be made to **reach** that desired state, and applies them for you.

This tool is the community fork of Terraform, created after HashiCorp relicensed Terraform in 2023. The syntax, provider registry, and CLI workflow are identical.

An OpenTofu project is made up of a few simple initial building blocks:

| Component | What it is | File in this lesson |
|---|---|---|
| 🔌 **Provider** | A plugin that knows how to talk to a specific platform. Think of it like the Ansible collection equivalent. | `provider.tf` |
| 📌 **Version constraints** | Tells OpenTofu which version of itself and the provider are required, so the project works the same for everyone. | `versions.tf` |
| 🔧 **Variables** | Named inputs to your project: like function arguments. Keep credentials and device-specific values out of the main code. | `variables.tf` |
| 🔑 **tfvars file** | A simple key=value file where you set the actual values for your variables. | `terraform.tfvars` |
| 🔍 **Data source** | A read-only query. It fetches the current state of something on the device without making any changes. | `read.tf` |
| 🏗️ **Resource** | A thing you want OpenTofu to create, manage, and eventually destroy. OpenTofu tracks it in the state file. | `create.tf` |

About the `Data Source` and `Resource` files, we shall do things with them via the following commands:

1. `tofu plan`: computes the diff between current state and desired state. Like the **Dry-Run** mode that we saw with Ansible.
2. `tofu apply`: executes create/update actions. This is the real commit!
3. `tofu destroy`: executes delete actions.

---

## ⚖️ Paradigm shift vs Ansible (and OpenTofu's imperativeness)

Both tools are often called "declarative", but they are declarative in different ways.

| Angle | Ansible (Session 03 lesson) | OpenTofu (this lesson) |
|---|---|---|
| Core unit | Ordered tasks in a playbook | Resources in a state graph |
| Idempotence scope | Per task/module rerun | Whole graph reconciliation |
| Execution model | Linear task runner | Planned action graph |
| Imperative side | Task order is explicit in YAML | Lifecycle commands are imperative (`tofu plan/apply/destroy`) |
| Deletion model | Explicit "absent/deleted" tasks | Remove from config or run `tofu destroy` - state drives deletion |

> With **Ansible** you write a list of steps to run "do this, then do that"

> With **OpenTofu** you declare what **the end result should look like**, and OpenTofu remembers what it created last time (the state file) to decide what to add, change, or remove next time you run it

---

## 🗂️ Today's lab

Install OpenTofu first:

> OpenTofu is a standalone binary, meaning, it cannot be installed inside a Python virtual environment.

Pick the right method for installing OpenTofu based on your host OS:

```bash
# macOS
brew install opentofu
```

```bash
# Linux — download and install the latest release manually
curl -Lo /tmp/tofu.zip https://github.com/opentofu/opentofu/releases/latest/download/tofu_linux_amd64.zip
unzip /tmp/tofu.zip -d /tmp/tofu
sudo mv /tmp/tofu/tofu /usr/local/bin/tofu
tofu version
```

```powershell
# Windows
winget install --id OpenTofu.OpenTofu
```

> For other Linux distros (rpm, deb packages) and additional install methods, see the [official install guide](https://opentofu.org/docs/intro/install/).

### DevNet Always-on Sandboxes
In this case, we will reuse the [IOS XR Always-on](https://devnetsandbox.cisco.com/DevNet/catalog/iosxr-always-on-public_iosxr-always-on-public) device, which provides a Cisco IOSXR shared device with SSH and some other cool features that we will use later on.

> This is a **shared environment**, meaning that multiple users can access it simultaneously. You may see other users' configurations, and they can see yours. Nevertheless, this environment resets to default settings everyday.

### 📄 Step 1: Setup files

We start by picking our **provider**. Cisco has plenty of providers for different products and platforms available [in this catalogue](https://registry.terraform.io/search/providers?namespace=CiscoDevNet). In this lab we use `CiscoDevNet/iosxr`.

We proceed to set it up in the **`versions.tf`** file. This tells OpenTofu which version of itself and which provider to use.

```hcl
# versions.tf
terraform {
  required_version = ">= 1.8.0"

  required_providers {
    iosxr = {
      source  = "CiscoDevNet/iosxr"
      version = "= 0.7.0"
    }
  }
}
```

- `required_version`: minimum OpenTofu version accepted.
- `source`: registry path for the Cisco IOS XR provider.
- `version`: minimum provider version accepted.

Second file is **`variables.tf`**. Here we declare every input variable used by the other files:

```hcl
# variables.tf
variable "iosxr_host"        { type = string }
variable "iosxr_username"    { type = string }
variable "iosxr_password"    { type = string; sensitive = true }
variable "demo_loopback_id"  { type = string; default = "123" }
variable "demo_loopback_ipv4"{ type = string; default = "10.123.123.1" }
variable "demo_loopback_mask"{ type = string; default = "255.255.255.255" }
```

- `sensitive = true` on the password tells OpenTofu to redact it from all output.
- The `loopback` variables have defaults so you can run the lab without passing extra flags.

We then move forward with **`provider.tf`**: it configures *how* OpenTofu connects to the device (credentials and transport):

```hcl
provider "iosxr" {
  host               = var.iosxr_host
  username           = var.iosxr_username
  password           = var.iosxr_password
  tls                = false
  verify_certificate = false
}
```

- `host` / `username` / `password`: read from variables so credentials never live in this file.
- `tls = false`: use plain gNMI for this DevNet sandbox endpoint.
- `verify_certificate = false`: keep certificate checks disabled (not used when `tls = false`).

> This is documented in the [official docs](https://registry.terraform.io/providers/CiscoDevNet/iosxr/latest/docs) of this specific provider.

Next is **`terraform.tfvars.example`**: the credentials template. Copy it to `terraform.tfvars` and fill in your DevNet Sandbox values.

```hcl
iosxr_host     = "sandbox-iosxr-1.cisco.com:57777"
iosxr_username = "replace_me"
iosxr_password = "replace_me"
```

> This provider uses gNMI (not SSH CLI), so using port `22` will not work here. The IOS XR Always-on sandbox gNMI endpoint is on port `57777`.

Once those values are set, initialise the project:

```bash
tofu init
```

`tofu init` reads `versions.tf`, downloads the declared provider binary into a local `.terraform/` folder, and locks the exact version in `.terraform.lock.hcl`. You only need to run it once (or again if you change the provider version).

If you get the following output, you're ready to start using OpenTofu!

```bash
Initializing the backend...

Initializing provider plugins...
- Reusing previous version of ciscodevnet/iosxr from the dependency lock file
- Using previously-installed ciscodevnet/iosxr v0.7.0

OpenTofu has been successfully initialized!
```

---

## 📖 Step 2: Read interface data (Ansible read equivalent)

In Ansible, we used `iosxr_command` for read-only checks. In Terraform, the read-only equivalent is a `data source`:

```hcl
# read.tf
data "iosxr_interface_loopback" "observed" {
  name = var.demo_loopback_id
  depends_on = [iosxr_interface_loopback.demo]
}

output "observed_loopback_description" {
  value = data.iosxr_interface_loopback.observed.description
}

output "observed_loopback_ipv4_address" {
  value = data.iosxr_interface_loopback.observed.ipv4_address
}
```

- `data "iosxr_interface_loopback" "observed"` reads an existing loopback from the device (read-only).
- `name = var.demo_loopback_id` tells OpenTofu which loopback to look for (this is one of the variables that we setup in the `variables.tf` file).
- `depends_on = [iosxr_interface_loopback.demo]` avoids a first-run `NotFound` error by reading only after the loopback is created.
- `output "observed_loopback_description"` prints the loopback description in command output so you can see what the device currently has.

Run:

```bash
tofu plan
```

This does not create resources. Instead, it queries device state and exposes attributes in outputs:

```bash
OpenTofu used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
 <= read (data resources)

OpenTofu will perform the following actions:

  # iosxr_interface_loopback.demo will be created
  + resource "iosxr_interface_loopback" "demo" {
      + description  = "CITNC_TERRAFORM_DEMO"
      + id           = (known after apply)
      + ipv4_address = "10.123.123.1"
      + ipv4_netmask = "255.255.255.255"
      + name         = "123"
      + shutdown     = false
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  ~ observed_loopback_description  = "CITNC_TERRAFORM_DEMO" -> (known after apply)
  ~ observed_loopback_ipv4_address = "10.123.123.1" -> (known after apply)
```

This is OpenTofu **literally** telling us what does it plan to do!

> **Notice that** you didn't need to tell OpenTofu which commands to run for checking if the interface exists or not. The resource figures everything by itself!

---

## ✍️ Step 3: Create loopback (Ansible create equivalent)

In Ansible we used `iosxr_interfaces` + `iosxr_l3_interfaces`. In Terraform we define a resource owned by state.

```hcl
# create.tf
resource "iosxr_interface_loopback" "demo" {
  name         = var.demo_loopback_id
  description  = "CITNC_TERRAFORM_DEMO"
  shutdown     = false
  ipv4_address = var.demo_loopback_ipv4
  ipv4_netmask = var.demo_loopback_mask
}
```

Apply:

```bash
tofu apply
```

On the first apply, you should see the resource creation and then the data source read:
```bash
OpenTofu used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create
 <= read (data resources)

OpenTofu will perform the following actions:

  # iosxr_interface_loopback.demo will be created
  + resource "iosxr_interface_loopback" "demo" {
      + description  = "CITNC_TERRAFORM_DEMO"
      + id           = (known after apply)
      + ipv4_address = "10.123.123.1"
      + ipv4_netmask = "255.255.255.255"
      + name         = "123"
      + shutdown     = false
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  ~ observed_loopback_description  = "CITNC_TERRAFORM_DEMO" -> (known after apply)
  ~ observed_loopback_ipv4_address = "10.123.123.1" -> (known after apply)

Do you want to perform these actions?
  OpenTofu will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

iosxr_interface_loopback.demo: Creating...
iosxr_interface_loopback.demo: Creation complete after 1s [id=Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]]
data.iosxr_interface_loopback.observed: Reading...
data.iosxr_interface_loopback.observed: Read complete after 0s [id=Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

After you explicitly say `yes`, the configuration is applied.

> **Notice that** yet again, you didn't need to specify the commands for creating a new interface. The resource figured everything alone!

Now, run `tofu apply` again and confirm the second run has no planned changes. That is your idempotence check in OpenTofu terms:

```bash
data.iosxr_interface_loopback.observed: Reading...
iosxr_interface_loopback.demo: Refreshing state... [id=Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]]
data.iosxr_interface_loopback.observed: Read complete after 1s [id=Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]]

No changes. Your infrastructure matches the configuration.

OpenTofu has compared your real infrastructure against your configuration and found no
differences, so no changes are needed.

Apply complete! Resources: 0 added, 0 changed, 0 destroyed.
```

---

## 🧹 Step 3: Delete loopback (Ansible delete equivalent)

Use this compliant plan (code-first deletion):

1. Open `create.tf`.
2. Delete the whole resource block below.
3. Open `read.tf` and remove the `depends_on` line (it references the resource you just removed).
4. In `read.tf`, remove the demo loopback data/output blocks too, so OpenTofu no longer tries to read a loopback that you are deleting.
5. Run `tofu plan` and verify it shows `1 to destroy`.
6. Run `tofu apply` and confirm with `yes`.

This is the exact block to remove from `create.tf`:

```hcl
resource "iosxr_interface_loopback" "demo" {
  name         = var.demo_loopback_id
  description  = "CITNC_TERRAFORM_DEMO"
  shutdown     = false
  ipv4_address = var.demo_loopback_ipv4
  ipv4_netmask = var.demo_loopback_mask
}
```

And remove this demo-read block from `read.tf`:

```hcl
data "iosxr_interface_loopback" "observed" {
  name = var.demo_loopback_id
  depends_on = [iosxr_interface_loopback.demo]
}

output "observed_loopback_description" {
  value = data.iosxr_interface_loopback.observed.description
}

output "observed_loopback_ipv4_address" {
  value = data.iosxr_interface_loopback.observed.ipv4_address
}
```

Execute a `tofu plan`, which shall give this result:

```bash
iosxr_interface_loopback.demo: Refreshing state... [id=Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]]

OpenTofu used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

OpenTofu will perform the following actions:

  # iosxr_interface_loopback.demo will be destroyed
  # (because iosxr_interface_loopback.demo is not in configuration)
  - resource "iosxr_interface_loopback" "demo" {
      - description  = "CITNC_TERRAFORM_DEMO" -> null
      - id           = "Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]" -> null
      - ipv4_address = "10.123.123.1" -> null
      - ipv4_netmask = "255.255.255.255" -> null
      - name         = "123" -> null
      - shutdown     = false -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Changes to Outputs:
  - observed_loopback_description  = "CITNC_TERRAFORM_DEMO" -> null
  - observed_loopback_ipv4_address = "10.123.123.1" -> null
```

Finally, issue a `tofu apply` that shall output this:

```bash
iosxr_interface_loopback.demo: Refreshing state... [id=Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]]

OpenTofu used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  - destroy

OpenTofu will perform the following actions:

  # iosxr_interface_loopback.demo will be destroyed
  # (because iosxr_interface_loopback.demo is not in configuration)
  - resource "iosxr_interface_loopback" "demo" {
      - description  = "CITNC_TERRAFORM_DEMO" -> null
      - id           = "Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]" -> null
      - ipv4_address = "10.123.123.1" -> null
      - ipv4_netmask = "255.255.255.255" -> null
      - name         = "123" -> null
      - shutdown     = false -> null
    }

Plan: 0 to add, 0 to change, 1 to destroy.

Changes to Outputs:
  - observed_loopback_description  = "CITNC_TERRAFORM_DEMO" -> null
  - observed_loopback_ipv4_address = "10.123.123.1" -> null

Do you want to perform these actions?
  OpenTofu will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

iosxr_interface_loopback.demo: Destroying... [id=Cisco-IOS-XR-um-interface-cfg:/interfaces/interface[interface-name=Loopback123]]
iosxr_interface_loopback.demo: Destruction complete after 1s

Apply complete! Resources: 0 added, 0 changed, 1 destroyed.
```

---

## 🧠 Concept Mapping

| Interface workflow | Ansible lesson | Terraform lesson |
|---|---|---|
| Read | `iosxr_command` show outputs | `data "iosxr_interface_loopback"` |
| Create | `iosxr_interfaces` + `iosxr_l3_interfaces` with `state: merged` | `resource "iosxr_interface_loopback"` + `tofu apply` |
| Delete | Resource modules with `state: deleted` | Remove resource from code + `tofu apply`, or `tofu destroy` |

---

## 🚀 What's Next

This extra lesson introduces a state-centric lifecycle model alongside the task-centric model from Ansible. Together, they help you choose the right automation tool based on whether you are orchestrating procedural tasks or managing long-lived infrastructure state.

OpenTofu and Ansible are complementary, not competing: Ansible excels at day-2 operational workflows, while OpenTofu manages the full lifecycle of infrastructure resources, including clean teardown, backed by a state record.

That is the bridge to API and model-driven patterns in **Session 03: Model-Driven Programmability**.
