# 🌐 Session 02 | Lesson 03: Ansible Basics with IOS XR
Topics: 📦 Inventory · ▶️ Playbooks · 🔁 Idempotence

---

## 🎯 By the end of this session you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 📦 Build a small Ansible inventory for Cisco IOS XR devices |
| 2 | ▶️ Explain how a playbook maps hosts, tasks, and modules into automation steps |
| 3 | 📖 Run safe read-only operational checks with a Cisco IOS XR command module |
| 4 | ✍️ Apply a configuration change with an idempotent Ansible task |
| 5 | 🔁 Prove why idempotence matters by rerunning the same playbook and comparing results |

---

## 🗺️ What is going on

<div align="center"><img src="../../images/citnc_banner_07.png" width="80%"/></div></br>

---

So far in Session 02, we have used pyATS to connect to devices, collect state, and validate changes. That works well when you want Python-first control and structured parsing.

Now we introduce a second style of automation: Ansible. Instead of writing Python control flow, we describe the target devices in an inventory and the intended actions in a playbook. This is a very common workflow in real operations teams because the automation becomes easy to read, easy to rerun, and easy to review.

For this lesson, we switch to Cisco IOS XR over SSH and use ready-made modules from the Cisco `cisco.iosxr` Ansible collection:

1. `cisco.iosxr.iosxr_command` for read-only operational checks.
2. `cisco.iosxr.iosxr_interfaces` and `cisco.iosxr.iosxr_l3_interfaces` for interface-focused configuration changes.

The key concept to watch is not just "did the playbook run?" but "does it behave safely when I run it again?" That is the heart of idempotence.

**🏅 Golden rule No.3:**
> A good automation task should converge the device to the intended state, not blindly push the same change forever.

---

## 🤖 Why Ansible here

Ansible is useful when you want to describe outcomes without writing a full Python program around every step.

For network automation, that usually means:

- An **inventory** that lists devices and connection variables.
- A **playbook** that lists tasks to run against a group of devices.
- A **module** that knows how to talk to a specific network platform.

In this lesson we use the Cisco collection for IOS XR. It gives us a platform-aware command module for reads and resource modules for interface/L3 writes in a desired-state style.

---

## 🗂️ Today's lab

### DevNet Always-on Sandboxes
In this case, we will use the [IOS XR Always-on](https://devnetsandbox.cisco.com/DevNet/catalog/iosxr-always-on-public_iosxr-always-on-public) device, which provides a Cisco IOSXR shared device with SSH and some other cool features that we will use later on.

> This is a **shared environment**, meaning that multiple users can access it simultaneously. You may see other users' configurations, and they can see yours. Nevertheless, this environment resets to default settings everyday.


### Virtual Environment
Reuse the virtual environment from the rest of Session 02:

```bash
cd session-02-interaction
source .venv/bin/activate
pip install -r requirements.txt
cd 03-ansible-basics
ansible-galaxy collection install -r collections/requirements.yml -p ./collections
```

A few important details about that last command:

- The Python package `ansible` gives you `ansible-playbook` and the base runtime.
- The Cisco IOS XR content is installed as an Ansible **collection**, not as a regular Python import.

> **📦 What is a collection?**
> A collection is a packaged bundle of Ansible modules, plugins, and roles published to [Ansible Galaxy](https://galaxy.ansible.com): the public registry for Ansible content, equivalent to PyPI for Python packages. `ansible-galaxy` is the CLI tool that fetches and installs them.

This command installs two collections from Galaxy:

| Collection | Maintained by | What it provides |
|---|---|---|
| `ansible.netcommon` | Ansible project | The `network_cli` SSH connection plugin: the transport layer that opens and maintains a persistent CLI session to any network device |
| `cisco.iosxr` | Cisco | The `iosxr_command`, `iosxr_interfaces`, and `iosxr_l3_interfaces` modules, plus IOS XR-specific prompt handling. It depends on `ansible.netcommon`, so both must be present |

If you check the file `collections/requirements.yml`, these are the collections that we are installing. Think about it as the `requirements.txt` that we've been using for Python libraries:

```yaml
# requirements.yml
collections:
  - name: ansible.netcommon
  - name: cisco.iosxr
```

When looking for a specific collection, browse [galaxy.ansible.com](https://galaxy.ansible.com) and search for the platform name (e.g., "iosxr") to find the official one.

---

## 📦 Step 2: Understand the inventory

The inventory for this lesson is intentionally small:

```yaml
# inventory.yml
all:
  children:
    iosxr:
      hosts:
        xrd-1:
          ansible_host: sandbox-iosxr-1.cisco.com
```

This means:

- `all` is the top-level inventory tree.
- `iosxr` is a group.
- `xrd-1` is a host alias.
- `ansible_host` is the real IP or DNS name Ansible should use. In our case, it is the one of the DevNet Sandbox.

Then we keep the shared connection settings in `group_vars/iosxr.yml`:

```yaml
ansible_connection: ansible.netcommon.network_cli
ansible_network_os: cisco.iosxr.iosxr
ansible_user: replace_me
ansible_password: replace_me
ansible_command_timeout: 60
```

Briefly, each variable does this:

- `ansible_connection`: selects the transport plugin (`network_cli`) so Ansible opens an SSH network-device session.
- `ansible_network_os`: tells Ansible which platform driver to use (IOS XR), so the right modules and command handling are applied.
- `ansible_user`: username used to log in to the device. You're given this one when booking the DevNet Sandbox!
- `ansible_password`: password for that user. Same as above!
- `ansible_command_timeout`: maximum seconds Ansible waits for a network command to finish before failing.

**Where do these come from?**

The first three variables (`ansible_connection`, `ansible_network_os`, `ansible_command_timeout`) are documented in the [Cisco IOS XR collection on Ansible Galaxy](https://galaxy.ansible.com/cisco/iosxr). The values are **platform-specific**: every platform has an official name for its network OS, and its collection documents which connection method and timeout to use.

The login credentials (`ansible_user`, `ansible_password`) come from your DevNet Sandbox booking confirmation email: look for "username" and "password", then copy them into this file.

> This separation is useful because the inventory states **who the devices are**, while `group_vars` states **how to talk to that platform**.

> Rename the file `iosxr.yml.example` as ``iosxr.yml` and populate the values `ansible_user` and `ansible_password` with your own.

---

## ▶️ Step 3: Run a read-only playbook

Our first playbook uses `cisco.iosxr.iosxr_command`, a ready-made module from the Cisco IOS XR collection:

```yaml
# playbooks/01_read_state.yml
- name: Read operational state from IOS XR
  hosts: iosxr
  gather_facts: false
  collections:
    - cisco.iosxr

  tasks:
    - name: Run show commands
      cisco.iosxr.iosxr_command:
        commands:
          - show version
          - show ipv4 interface brief
      register: iosxr_show

    - name: Print command results
      ansible.builtin.debug:
        var: iosxr_show.stdout_lines
```

**Playbook structure:**

| Key | Purpose |
|---|---|
| `name` | Human-readable description of what the playbook does |
| `hosts` | The host group (from inventory) to run tasks against |
| `gather_facts: false` | Skip fact gathering (not useful for network devices) |
| `collections` | Load the modules we need (in this case, `cisco.iosxr`) |
| `tasks` | List of actions to execute in order |
| `register` | Store task output in a variable for later use |
| `debug` | Print output to the terminal |

> The parameters for using `cisco.iosxr.iosxr_command` and other useful modules can be found in the [official documentation of this collection](https://galaxy.ansible.com/ui/repo/published/cisco/iosxr/docs/).

Run it like this:

```bash
ansible-playbook playbooks/01_read_state.yml
```

You will get something like this:

```bash
PLAY [Read operational state from IOS XR] *********************************************************************************************************************************************

TASK [Run show commands] **************************************************************************************************************************************************************
ok: [xrd-1]

TASK [Print command results] **********************************************************************************************************************************************************
ok: [xrd-1] => {
    "iosxr_show.stdout_lines": [
        [
            "Cisco IOS XR Software, Version 25.3.1 LNT",
            "Copyright (c) 2013-2025 by Cisco Systems, Inc.",
            "",
            "Build Information:",
            " Built By     : cisco",
            " Built On     : Wed Sep 10 14:59:44 UTC 2025",
            " Build Host   : iox-lnx-034",
            " Workspace    : /auto/srcarchive12/prod/25.3.1/xrd-control-plane/ws/",
            " Version      : 25.3.1",
            " Label        : 25.3.1",
            "",
            "cisco XRd Control Plane",
            "cisco XRd-CP-C-01 processor with 24GB of memory",
            "xrd-1 uptime is 1 day, 3 hours, 1 minute",
            "XRd Control Plane Container"
        ],
        [
            "Interface                      IP-Address      Status          Protocol Vrf-Name",
            "Loopback10                     10.10.10.1      Up              Up       default ",
            "MgmtEth0/RP0/CPU0/0            10.10.20.101    Up              Up       default ",
            "GigabitEthernet0/0/0/0         192.168.1.10    Up              Up       default ",
            "GigabitEthernet0/0/0/1         192.168.1.14    Up              Up       default"
        ]
    ]
}

PLAY RECAP ****************************************************************************************************************************************************************************
xrd-1                      : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0 
```

This is a pure **read** workflow. No config mode, no commit, no drift risk. It is the Ansible equivalent of the read-only pyATS workflows you already introduced.

---

## ✍️ Step 4: Run an idempotent write playbook

Now, similar to what we did with pyATS, we want to create new interfaces in the devices of our inventory.
Instead of using raw CLI commands like we've done so far, we will use the dedicated modules `cisco.iosxr.iosxr_interfaces` and `cisco.iosxr.iosxr_l3_interfaces`:

```yaml
# playbooks/02_configure_loopback.yml
- name: Ensure a demo loopback exists on IOS XR
  hosts: iosxr
  gather_facts: false
  collections:
    - cisco.iosxr

  vars:
    demo_loopback_name: Loopback123
    demo_loopback_description: CITNC_ANSIBLE_DEMO
    demo_loopback_ipv4: 10.123.123.1/32

  tasks:
    - name: Ensure loopback interface attributes are present
      cisco.iosxr.iosxr_interfaces:
        config:
          - name: "{{ demo_loopback_name }}"
            description: "{{ demo_loopback_description }}"
            enabled: true
        state: merged
      register: interface_result

    - name: Ensure loopback IPv4 address is present
      cisco.iosxr.iosxr_l3_interfaces:
        config:
          - name: "{{ demo_loopback_name }}"
            ipv4:
              - address: "{{ demo_loopback_ipv4 }}"
        state: merged
      register: l3_result

    - name: Show whether the device changed
      ansible.builtin.debug:
        msg:
          - "interface_changed={{ interface_result.changed }}"
          - "l3_changed={{ l3_result.changed }}"

    - name: Verify resulting interface configuration
      cisco.iosxr.iosxr_command:
        commands:
          - show running-config interface {{ demo_loopback_name }}
      register: verification

    - name: Print verification output
      ansible.builtin.debug:
        var: verification.stdout_lines
```

Task-by-task (quick view):

- `Ensure loopback interface attributes are present`: creates/updates the loopback interface metadata (description/admin state).
- `Ensure loopback IPv4 address is present`: creates/updates the loopback IPv4 address.
- `Show whether the device changed`: prints idempotence signals from both write tasks.
- `Verify resulting interface configuration`: runs a read command to validate final device state.
- `Print verification output`: prints the verification command output.

⚠️ `state: merged` means __"add/update only what is declared in `config` and keep everything else as-is".__

> Why two tasks for the same interface?

- `iosxr_interfaces` manages interface attributes (for example `description`, `enabled`).
- `iosxr_l3_interfaces` manages Layer-3 addressing (for example `ipv4`).

They are different resource models, so they are usually kept as separate tasks for clarity and predictable idempotence.
If you really want a single task, you can switch to `cisco.iosxr.iosxr_config` and push both lines together, but you lose the resource-model separation.

## 🏃‍♂️ Step 4.1: Dry-Run - Or better checking before breaking the network

Ansible allows us to run our playbooks to evaluate what would change in the target device configurations without actually changing anything.

In our case, if we run the playbook with the following options:

```bash
ansible-playbook playbooks/02_configure_loopback.yml --check --diff
```

We get the following output:

```bash
PLAY [Ensure a demo loopback exists on IOS XR] ****************************************************************************************************************************************

TASK [Ensure loopback interface attributes are present] *******************************************************************************************************************************
changed: [xrd-1]

TASK [Ensure loopback IPv4 address is present] ****************************************************************************************************************************************
changed: [xrd-1]

TASK [Show whether the device changed] ************************************************************************************************************************************************
ok: [xrd-1] => {
    "msg": [
        "interface_changed=True",
        "l3_changed=True"
    ]
}

TASK [Verify resulting interface configuration] ***************************************************************************************************************************************
ok: [xrd-1]

TASK [Print verification output] ******************************************************************************************************************************************************
ok: [xrd-1] => {
    "verification.stdout_lines": [
        [
            "% No such configuration item(s)"
        ]
    ]
}

PLAY RECAP ****************************************************************************************************************************************************************************
xrd-1                      : ok=5    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

You can see that the print indicates that there will be changes, case this playbook is applied. However, it was **NOT** applied, given that the output of task `Print verification output` is empty.

> One important caveat: some modules/platforms may still need to read live device state and not every module provides full diff details in check mode. So treat it as “best-effort preview,” not a perfect guarantee.

## 🏃‍♂️ Step 4.2: Running the playbook for real 

Now, let's apply the playbook for good without the flags:

```bash
ansible-playbook playbooks/02_configure_loopback.yml
```

On the first run, Ansible should normally report `changed=true` because the loopback is missing.

```bash
PLAY [Ensure a demo loopback exists on IOS XR] ************************************************************************************************************************************************************************************

TASK [Ensure loopback interface attributes are present] ***************************************************************************************************************************************************************************
changed: [xrd-1]

TASK [Ensure loopback IPv4 address is present] ************************************************************************************************************************************************************************************
changed: [xrd-1]

TASK [Show whether the device changed] ********************************************************************************************************************************************************************************************
ok: [xrd-1] => {
    "msg": [
        "interface_changed=True",
        "l3_changed=True"
    ]
}

TASK [Verify resulting interface configuration] ***********************************************************************************************************************************************************************************
ok: [xrd-1]

TASK [Print verification output] **************************************************************************************************************************************************************************************************
ok: [xrd-1] => {
    "verification.stdout_lines": [
        [
            "interface Loopback123",
            " description CITNC_ANSIBLE_DEMO",
            " ipv4 address 10.123.123.1 255.255.255.255",
            "!"
        ]
    ]
}

PLAY RECAP ************************************************************************************************************************************************************************************************************************
xrd-1                      : ok=5    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0   
```

On the second run, with the same intended state already present, Ansible should report `changed=false`.

```bash
PLAY [Ensure a demo loopback exists on IOS XR] ************************************************************************************************************************************************************************************

TASK [Ensure loopback interface attributes are present] ***************************************************************************************************************************************************************************
ok: [xrd-1]

TASK [Ensure loopback IPv4 address is present] ************************************************************************************************************************************************************************************
ok: [xrd-1]

TASK [Show whether the device changed] ********************************************************************************************************************************************************************************************
ok: [xrd-1] => {
    "msg": [
        "interface_changed=False",
        "l3_changed=False"
    ]
}

TASK [Verify resulting interface configuration] ***********************************************************************************************************************************************************************************
ok: [xrd-1]

TASK [Print verification output] **************************************************************************************************************************************************************************************************
ok: [xrd-1] => {
    "verification.stdout_lines": [
        [
            "interface Loopback123",
            " description CITNC_ANSIBLE_DEMO",
            " ipv4 address 10.123.123.1 255.255.255.255",
            "!"
        ]
    ]
}

PLAY RECAP ************************************************************************************************************************************************************************************************************************
xrd-1                      : ok=5    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0  
```

That second run is the teaching moment: the playbook is not "a list of commands to send". It is a **desired-state declaration** checked against the **current running configuration**.

---

## 🧹 Optional cleanup

If you want to remove the demo loopback after the exercise, use the cleanup playbook included in this folder. This version uses the same modules `cisco.iosxr.iosxr_l3_interfaces` and `cisco.iosxr.iosxr_interfaces`:

```yaml
# 03_remove_loopback.yml
- name: Remove the demo loopback from IOS XR
  hosts: iosxr
  gather_facts: false
  collections:
    - cisco.iosxr

  vars:
    demo_loopback_name: Loopback123

  tasks:
    - name: Remove loopback IPv4 address
      cisco.iosxr.iosxr_l3_interfaces:
        config:
          - name: "{{ demo_loopback_name }}"
        state: deleted
      register: cleanup_l3_result

    - name: Remove loopback interface attributes
      cisco.iosxr.iosxr_interfaces:
        config:
          - name: "{{ demo_loopback_name }}"
        state: deleted
      register: cleanup_if_result

    - name: Show cleanup result
      ansible.builtin.debug:
        msg:
          - "l3_changed={{ cleanup_l3_result.changed }}"
          - "interface_changed={{ cleanup_if_result.changed }}"
```

Very briefly:

- `state: deleted` in `iosxr_l3_interfaces`: removes L3 attributes (the interface IP in this case).
- `state: deleted` in `iosxr_interfaces`: removes interface-level attributes managed by that resource model.
- The final debug prints whether either cleanup task had to change device state.

Let's execute it as follows:

```bash
ansible-playbook playbooks/03_remove_loopback.yml
```

Finally, we get the following output:

```bash
PLAY [Remove the demo loopback from IOS XR] ***************************************************************************************************************************************************************************************

TASK [Remove loopback IPv4 address] ***********************************************************************************************************************************************************************************************
changed: [xrd-1]

TASK [Remove loopback interface attributes] ***************************************************************************************************************************************************************************************
changed: [xrd-1]

TASK [Show cleanup result] ********************************************************************************************************************************************************************************************************
ok: [xrd-1] => {
    "msg": [
        "l3_changed=True",
        "interface_changed=True"
    ]
}

PLAY RECAP ************************************************************************************************************************************************************************************************************************
xrd-1                      : ok=3    changed=2    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0  
```

This results in cleanup of the loopback configuration in the same idempotent style used in the write playbook.

---

## 🧠 Concept Mapping

| Ansible concept | Operations equivalent |
|---|---|
| Inventory | Your list of devices and how to reach them |
| Playbook | The runbook written in YAML |
| Module | The platform-aware action that knows what to do |
| Idempotence | "Reach the target state once, then stop changing things" |
| Check mode | "Tell me what would change before you touch anything" |

---

## ⚖️ Ansible vs pyATS (When to use which)

| Option | Use it when | Why |
|---|---|---|
| **Ansible playbooks** | You want fast, repeatable operations tasks (read checks, standard config changes, day-2 automation) | Declarative workflow, easy reruns, great for team runbooks |
| **pyATS Python scripts** | You need custom logic, complex validations, parsing-heavy workflows, or conditional remediation | Full Python control and richer programming flexibility |

Practical rule of thumb: start with **Ansible** for common operational workflows, and use **pyATS** when you need deeper custom logic or advanced testing behavior.

---

## 🚀 What's Next

This lesson introduces the declarative mindset: describe the intended state, let the tool compare, and prove the outcome. That is the bridge from CLI automation into model-driven automation, where the same idea appears again with APIs, data models, and protocol-specific payloads.

That is the bridge to **Session 03: Model-Driven Programmability**.