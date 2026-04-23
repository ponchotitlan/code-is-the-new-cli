# 🏠 Session 02 Interaction: Homework Assignment
Topics: 🧪 pyATS write/read/delete · 📦 Ansible resource modules · 🛡️ Idempotence in shared labs

---

In Session 02 you practiced two automation styles against network devices:

- **Python-first control** with pyATS
- **Declarative workflows** with Ansible

Now it is your turn to implement both approaches on the same Cisco IOS XR sandbox and prove that they reach the same outcome safely.

This homework is designed to be **small, safe, and reversible**.

**🏅 Your golden rule:**
> In a shared sandbox, every change you make must be easy to verify and easy to remove.

---

## 📋 Scenario

You will book the **IOS XR Always-On Sandbox** and automate a tiny non-intrusive config lifecycle:

1. **Create** a temporary IPv4 ACL object.
2. **Read/verify** that the ACL is present with the expected entry.
3. **Delete** the ACL and confirm cleanup.

You must do this twice:

- first with **pyATS**
- then with **Ansible** using the official `cisco.iosxr` collection docs

To reduce collisions in the shared environment, use a unique ACL name and entry:

- ACL name: `CITNC-HW-ACL-<your-github-username>-<XX>`
- ACL entry: permit one TEST-NET source (for example `198.51.100.<XX>/32`) to any destination

This is intentionally non-intrusive because the ACL is **not applied to any interface**. You only create and remove the object.

---

## 1. Book and Prepare the Sandbox

Book the [IOS XR Always-On Sandbox](https://devnetsandbox.cisco.com/DevNet/catalog/iosxr-always-on-public_iosxr-always-on-public).

Create or reuse your Session 02 working environment:

```bash
cd session-02-interaction
source .venv/bin/activate
pip install -r requirements.txt
cd 03-ansible-basics
ansible-galaxy collection install -r collections/requirements.yml -p ./collections
```

Set your credentials in `group_vars/iosxr.yml` for Ansible and in your pyATS inventory file.

---

## 2. pyATS Task (Write, Read, Delete)

Create a script named `homework_pyats_acl_lifecycle.py` inside `session-02-interaction/homework`.

### pyATS requirements

Your script must:

1. Load inventory/testbed data from a YAML file.
2. Connect to IOS XR device.
3. Apply the demo ACL object (create).
4. Retrieve and validate config using a read command.
5. Remove the demo ACL object (delete).
6. Validate that it no longer exists.
7. Print clear PASS/FAIL style messages for each phase.

### Minimum structure requirements

- At least **4 named functions**.
- **Type hints** on all function signatures.
- **Docstring** on all functions.
- A `main()` entry point.
- Use `try/except/finally` so the device disconnect is always attempted.

### Suggested read checks

- `show running-config ipv4 access-list <acl-name>`
- Confirm the ACL name/entry is present after create.
- Confirm the ACL is absent after delete.

---

## 3. Ansible Task (Do the same lifecycle)

Using the official docs of the `cisco.iosxr` collection, create playbooks in `session-02-interaction/homework/ansible/` that perform the exact same lifecycle.

### Required playbooks

- `01_create_acl.yml`
- `02_verify_acl.yml`
- `03_delete_acl.yml`
- `04_verify_deleted.yml`

### Ansible requirements

- Use `cisco.iosxr.iosxr_acls` for create/delete states.
- Use `cisco.iosxr.iosxr_command` for verification.
- Keep variables (`acl name`, `source prefix`) in one place (vars file or play vars).
- Demonstrate idempotence:
  - Run create playbook twice and show second run is unchanged.

> You may still use `iosxr_config` for comparison experiments, but your final homework solution must use resource modules for create/delete.

---

## 4. Evidence and Comparison

Create a short report file:

- `session-02-interaction/homework/HW_REPORT.md`

Include:

1. Sandbox URL used and timestamp.
2. The exact ACL name and source prefix you chose.
3. pyATS run output snippets (create/read/delete/read).
4. Ansible run output snippets (create/verify/delete/verify).
5. One paragraph: **When would you choose pyATS vs Ansible for this type of task?**

---

## 5. Git Workflow Requirements

Complete homework in your own repository using at least **2 feature branches**:

- `feature/hw-pyats-lifecycle`
- `feature/hw-ansible-lifecycle`

Each branch must have at least **2 commits** following Conventional Commits.

Merge through Pull Requests into `main`.

---

## 📬 Submission to this Course Repository

Inside `session-02-interaction/homework`, create:

- `submission-<your-github-username>.md`

Use this format:

```markdown
# Homework Submission: Session 02 Interaction

**GitHub username:** <your-username>
**Homework repository:** <link>
**Sandbox used:** <IOS XR Always-On URL>
**ACL name used:** <e.g., CITNC-HW-ACL-alice-37>
**Source prefix used:** <e.g., 198.51.100.37/32>
**Most challenging part:** <one sentence>
```

Then open a PR to this repository using title:

`hw(session-02): submission from <your-github-username>`

---

## ✅ Checklist Before Submitting

| # | Item |
|:---:|:---|
| 1 | pyATS script exists and performs ACL create/read/delete/read |
| 2 | pyATS script includes functions, type hints, docstrings, and `main()` |
| 3 | pyATS script uses `try/except/finally` with disconnect handling |
| 4 | Ansible create/verify/delete/verify playbooks exist |
| 5 | Ansible solution uses `iosxr_acls` + `iosxr_command` |
| 6 | Ansible idempotence shown (second create run unchanged) |
| 7 | `HW_REPORT.md` includes evidence for both approaches |
| 8 | At least 2 feature branches merged via PRs |
| 9 | Conventional Commit messages used |
| 10 | `submission-<username>.md` added and PR opened to this repo |

---

## 🧠 Hints

- Start from the Session 02 examples and adapt, do not copy blindly.
- Use a unique ACL name to avoid stepping on other users in the shared sandbox.
- Keep every task reversible.
- If parser support is missing in pyATS for your chosen command, fallback to raw output checks.
- For Ansible dry-run preview, use:
  - `ansible-playbook <playbook>.yml --check --diff`
