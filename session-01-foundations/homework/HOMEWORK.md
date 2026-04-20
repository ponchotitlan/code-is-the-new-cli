# 🏠 Session 01 Foundations: Homework Assignment
Topics: 🗂️ Git workflow · 🧩 Jinja templates · 🐍 Python tooling · 📄 Structured data

---

Alice and Bob built the branch site automation workflow together. Now it is your turn.

You are a network engineer at a fictional company. Your manager has asked you to automate the configuration rollout for a new set of devices. You get to pick the device type: it could be switches, firewalls, wireless access points, or anything else you work with day to day.

Your job is to build a small but complete automation workflow: a Jinja2 template, a structured inventory, and a Python renderer that puts it all together, just like the team did in Sessions 01 through 04.

This version is intentionally simpler and beginner-friendly:

- Start from a very small config example.
- First identify what should change between devices.
- Then turn those changing values into Jinja placeholders.
- Then build inventories and render device configs.

**🏅 Your golden rule:**
> Do not copy the session files. Build your own scenario with your own device type and your own variable names.

---

## 📋 Requirements

### 1. Create your own GitHub repository

Create a **public** repository on your GitHub account named `cli-to-code-labs-<your-github-username>` (e.g. `cli-to-code-labs-alice`). You will keep adding to this repository as the course progresses, so treat it as a living record of your automation work.

Clone it locally and work from there:

```bash
git clone git@github.com:<your-username>/cli-to-code-labs-<your-github-username>.git
cd cli-to-code-labs-<your-github-username>
```

---

### 2. Build the Jinja2 template

Here is a real Cisco IOS switch configuration for a site called **NYC**. This is Device A:

```
! ============================
! Cisco IOS Switch — NYC Site
! ============================
hostname SW-NYC-01
!
! Management interface
interface Vlan1
 ip address 10.10.1.11 255.255.255.0
 no shutdown
!
ip default-gateway 10.10.1.1
!
! User VLAN
vlan 10
 name USERS-NYC
!
! SNMP
snmp-server community public RO
!
! NTP
ntp server 10.0.0.1
!
end
```

**Your job:** look at this config and ask: *"If this were the LAX site (Device B), which values would need to change?"*

Make a short list of those changing values — for example:

| What changes | Device A (NYC) | Device B (LAX) |
|---|---|---|
| Hostname | `SW-NYC-01` | `SW-LAX-01` |
| Management IP | `10.10.1.11` | `10.10.2.11` |
| Default gateway | `10.10.1.1` | `10.10.2.1` |
| VLAN name | `USERS-NYC` | `USERS-LAX` |

Everything else stays the same on all switches — those lines remain **static** in the template.

Once you have your list, turn those changing values into Jinja2 placeholders to create `device-template.j2`.

**Requirements for your template file:**

- At least **4 Jinja2 placeholders** with meaningful names (e.g. `{{ HOSTNAME }}`, `{{ MGMT_IP }}`, `{{ VLAN_NAME }}`).
- At least **4 static configuration lines** that do not change between devices.
- Inline `!` comments that explain what each section does.

> Tip: If a value is identical on every switch, do NOT make it a placeholder — keep it as a static line.

---

### 3. Create the structured inventory

Create **three inventory files** for the same set of devices:

- `inventory.csv`: at least **3 device records** in CSV format.
- `inventory.json`: at least **3 device records** in JSON format.
- `inventory.xml`: the same **3 device records** in XML format.

All files must use the same field names as the placeholders in your Jinja2 template.

All three files must contain the same 3 devices.

**CSV format hint:**

```csv
HOSTNAME,MGMT_IP,MGMT_MASK,VLAN_ID,VLAN_NAME,DEFAULT_GW
SW-NYC-01,10.10.1.11,255.255.255.0,10,USERS,10.10.1.1
```

**JSON format hint:**

```json
[
  {
    "HOSTNAME": "SW-NYC-01",
    "MGMT_IP": "10.10.1.11",
    "SITE_CODE": "NYC"
  }
]
```

**XML format hint:**

```xml
<inventory>
  <device>
    <HOSTNAME>SW-NYC-01</HOSTNAME>
    <MGMT_IP>10.10.1.11</MGMT_IP>
    <SITE_CODE>NYC</SITE_CODE>
  </device>
</inventory>
```

---

### 4. Write the Python renderer tool

Create a file called `config_renderer.py`. It must:

- Be split into **at least 3 named functions** (e.g. `load_template`, `load_inventory`, `render_configs`, `main`).
- Include **type hints** on every function signature.
- Include a **docstring** on every function.
- Accept the following **CLI arguments** via `argparse`:
  - `--template`: path to the `.j2` template file (required)
  - `--inventory`: path to the inventory file (required)
  - `--format`: inventory format, either `csv`, `json`, or `xml` (required)
  - `--output-dir`: output directory for rendered configs (optional, default `./rendered`)
- Print a confirmation line for each file rendered.
- Create the output directory if it does not already exist.

### ⭐ Bonus requirement (very important)

Add file error handling for the inventory path:

- If the path provided to `--inventory` does not exist, your code must handle it with `try/except`.
- Inside the `except` block, raise a `FileNotFoundError` with a clear message.

Please **research what `try/except` means in Python** and apply it in your renderer.

Test that `--help` works and shows all arguments with descriptions.

---

### 5. Use Git branches and commits properly

Do your work in at least **2 feature branches** before merging into `main`. For example:

- `feature/template-and-inventory`: the `.j2` template and the three inventory files.
- `feature/renderer`: the `config_renderer.py` tool.

Each branch must have at least **2 commits** with messages that follow the Conventional Commits format from Session 01.

Before merging each branch into `main`, open a **Pull Request** on your own repository and merge it there.

---

### 6. Add a short README to your repository

Create a `README.md` at the root of your repository with:

- The device type you chose and a one-sentence explanation of the scenario.
- Instructions to set up the virtual environment and install dependencies.
- The exact commands to run the renderer with the CSV, JSON, and XML inventories.
- Example output (copy the terminal output after a successful run).

---

## 📬 Submitting Your Homework

Once your repository is ready and all branches are merged into `main`, submit your work by opening a **Pull Request to this repository** (`code-is-the-new-cli`).

### Steps

1. **Fork** this repository to your GitHub account.
2. In your fork, create a branch named `hw/session-01-<your-github-username>`.
3. Inside `session-01-foundations/homework`, create a single file called `submission-<your-github-username>.md` with the following content:

```markdown
# Homework Submission: Session 01 Foundations

**GitHub username:** <your-username>
**Homework repository:** <link to your cli-to-code-labs-<your-username> repository>
**Device type chosen:** <e.g. "Cisco NX-OS VPC switch">
**What I found most challenging:** <one sentence>
```

5. Commit and push the branch to your fork.
6. Open a **Pull Request** from your fork's branch to the `main` branch of `code-is-the-new-cli`.
7. Use the PR title format: `hw(session-01): submission from <your-github-username>`

> Your homework repository must be **public** so it can be reviewed.

---

## ✅ Checklist Before You Submit

Before opening the PR, verify that your homework repository has all of these:

| # | Item |
|:---:|:---|
| 1 | `device-template.j2` with at least 4 placeholders and 4 static lines |
| 2 | `inventory.csv` with at least 3 device records |
| 3 | `inventory.json` with the same 3 device records |
| 4 | `inventory.xml` with the same 3 device records |
| 5 | `config_renderer.py` with functions, type hints, docstrings, and argparse |
| 6 | `--help` output looks correct and lists all arguments |
| 7 | Renderer runs successfully with `--format csv`, `--format json`, and `--format xml` |
| 8 | Bonus: `try/except` handles missing inventory path and raises `FileNotFoundError` |
| 9 | At least 2 feature branches merged via PRs into `main` |
| 10 | Commit messages follow Conventional Commits format |
| 11 | `README.md` with scenario description and run instructions |
| 12 | `submission.md` added to this repo via a fork PR |

---

## 🧠 Hints and Tips

- Reuse the `requirements.txt` and virtual environment from `session-01-foundations/`: no need to create a new one.
- If you are not sure which device type to pick, choose a **Cisco IOS switch** (not a router) and focus on VLANs and trunk ports instead of routing.
- Start simple: one hostname line, one management interface section, one VLAN section can be enough.
- The XML root element can be anything (e.g. `<inventory>`, `<devices>`, `<site>`), just make sure your parser looks for the right tag.
- For CSV, the first row is the header and must match your placeholder names exactly.
- Run `python config_renderer.py --help` before anything else. If it prints cleanly, the argparse wiring is correct.
- If you are new to Python error handling, search: "Python try except FileNotFoundError" and implement that exact pattern.
- Make small, focused commits. A commit that says `feat(template): add VLAN interface stanza` is better than one that says `add everything`.
