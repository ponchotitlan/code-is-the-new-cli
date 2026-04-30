# 🏠 Session 03 Models: Homework Assignment
Topics: 🧭 YANG Suite model discovery · 🔌 NETCONF with ncclient · 🛡️ Safe ACL lifecycle in shared labs

---

In Session 03 you practiced all about model-driven workflows.

Now it is your turn to combine two key skills on the same IOS XR sandbox:

- **Explore device models and payloads** with Cisco YANG Suite
- **Automate configuration lifecycle** with Python + `ncclient` over NETCONF

---

## 📋 Scenario

You will use the **IOS XR Always-On Sandbox** and perform this ACL object lifecycle:

1. **Read all ACLs** currently on the device.
2. **Create** one temporary IPv4 ACL object.
3. **Read/verify** that your ACL exists and contains the expected entry.
4. **Delete** the temporary ACL object.
5. **Read/verify** that your ACL no longer exists.

You must use:

- **Cisco YANG Suite** to identify/validate the YANG model path and payload shape.
- **Python `ncclient`** to execute NETCONF operations (`get-config`/`edit-config`).

To reduce collisions in the shared environment, use a unique ACL name and entry:

- ACL name: `CITNC-HW-ACL-<your-github-username>-<XX>` - CITNC stands for "Code is the New CLI". Sorry, I couldn't think of anything more creative
- ACL entry: permit one TEST-NET source (for example `198.51.100.<XX>/32`) to any destination

This is intentionally non-intrusive because the ACL is **not applied to any interface**. You only create and remove the object.

---

## 1. Create Your Own Repository

Before starting, you must create a **new personal repository** on GitHub to hold your homework work.

1. Create a new personal GitHub repository named however you like.
2. Clone it locally and set up your working directory structure:
   ```bash
   git clone https://github.com/<your-username>/<your-repository>.git
   cd <your-repository>
   ```
3. All scripts, reports, and evidence will live in this repository.
4. At submission time, you will **fork** the course repository and add only a metadata file linking to your work.

---

## 2. Book and Prepare the Sandbox

Book the [IOS XR Always-On Sandbox](https://devnetsandbox.cisco.com/DevNet/catalog/iosxr-always-on-public_iosxr-always-on-public).

Create or reuse your Session 03 virtual environment:

```bash
cd session-03-models
source .venv/bin/activate
pip install -r requirements.txt
```

Make sure you have `yangsuite` and `ncclient` in your virtual environment.

Set your device credentials/host details in your script or inventory variables.

---

## 3. YANG Suite Task (Model Discovery and Payload Validation)

Use Cisco YANG Suite to prepare your NETCONF implementation.

### YANG Suite requirements

You must:

1. Connect YANG Suite to the IOS XR sandbox device profile.
2. Identify the ACL YANG model/path used for IPv4 ACL definitions.
3. Retrieve ACL data (or running config subtree) to confirm your filter path.
4. Build/validate sample payloads for:
   - ACL create/update via `edit-config`
   - ACL deletion via `edit-config` with delete/remove operation
5. Capture evidence screenshots/snippets you used to guide your script.

### Suggested evidence from YANG Suite

- Model/path used for ACL list retrieval.
- Example XML filter for reading ACLs.
- Example XML payload for create.
- Example XML payload for delete.

---

## 4. Python NETCONF Task (Read, Create, Verify, Delete, Verify)

In your own repository, create a script named `homework_netconf_acl_lifecycle.py`.

### Python NETCONF requirements

Your script must:

1. Connect to IOS XR using `ncclient.manager.connect`.
2. Retrieve ACL config/state and print discovered ACL names (read all ACLs).
3. Create your unique demo ACL object with one permit entry (`edit-config`).
4. Retrieve ACL data again and validate your ACL exists.
5. Delete your demo ACL object (`edit-config`).
6. Retrieve ACL data one final time and validate your ACL is absent.
7. Print clear PASS/FAIL style messages for each phase.

### Minimum structure requirements

- Use **functions**.
- **Type hints** on all function signatures.
- **Docstring** on all functions.
- A `main()` entry point.
- Use `try/except/finally` so NETCONF session close is always attempted.

### NETCONF operation expectations

- Use `<get-config>` with a subtree filter (or equivalent) to retrieve ACLs.
- Use `<edit-config>` targeting `running` for create and delete actions.
- Confirm success by checking returned XML/result and follow-up read verification.

---

## 5. Evidence and Comparison

In your own repository, create a short report file named `HW_REPORT.md`.

Include:

1. Sandbox URL used and timestamp.
2. The exact ACL name and source prefix you chose.
3. YANG Suite evidence snippets/screenshots (path/filter/payload).
4. Python run output snippets (read/create/read/delete/read).
5. One paragraph: **How did YANG Suite help you build safer NETCONF automation with ncclient?**

---

## 📬 Submission to this Course Repository

1. **In your own repository**, complete all work (script, report, and commits).
2. **Fork** this course repository on GitHub.
3. Inside the forked repo, create a file:
   - `session-03-models/homework/submission-<your-github-username>.md`

Use this format:

```markdown
# Homework Submission: Session 03 Models

**GitHub username:** <your-username>
**Homework repository:** <link-to-your-repo>
**Sandbox used:** <IOS XR Always-On URL>
**ACL name used:** <e.g., CITNC-HW-ACL-alice-37>
**Source prefix used:** <e.g., 198.51.100.37/32>
**Most challenging part:** <one sentence>
```

4. Open a **Pull Request** to the main course repository using title:
   - `hw(session-03): submission from <your-github-username>`

The PR should only add/modify the `submission-<your-github-username>.md` file. All actual work remains in your own repository.

---

## ✅ Checklist Before Submitting

| # | Item |
|:---:|:---|
| 1 | YANG Suite model/path for IOS XR ACLs identified and documented |
| 2 | YANG Suite evidence for read/create/delete payload planning included |
| 3 | Python NETCONF script exists and performs read/create/read/delete/read |
| 4 | Script includes functions, type hints, docstrings, and `main()` |
| 5 | Script uses `try/except/finally` with session close handling |
| 6 | ACL creation verified via follow-up NETCONF read |
| 7 | ACL deletion verified via follow-up NETCONF read |
| 8 | `HW_REPORT.md` in your own repo includes YANG Suite + Python evidence |
| 9 | Conventional Commit messages used in your own repo |
| 10 | Your own repo is public/shared with course instructors |
| 11 | `submission-<username>.md` added to forked course repo and PR opened |

---

## 🧠 Hints

- Start from Session 03 NETCONF examples and adapt, do not copy blindly.
- Build your XML payload shape from YANG Suite first, then script it in Python.
- Use a unique ACL name to avoid collisions in the shared sandbox.
- Keep every task reversible.
- If one XPath/filter is too broad, refine subtree filters for faster and clearer verification.
