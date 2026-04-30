# 🌐 Session 02 | Lesson 02: Change Validation with Snapshots and Diffs
Topics: 📸 Before/after state capture · 🔄 Structured comparison · 🗂️ Evidence reports

---

## 🎯 By the end of this session you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 📸 Capture parsed device state as JSON snapshots |
| 2 | 🔄 Compare before and after snapshots to identify exact changes |
| 3 | 🎯 Apply a remediation and prove it worked using snapshot diffs |
| 4 | 🗂️ Generate machine-readable change reports for audits and records |
| 5 | ♻️ Reuse snapshot capture for any validation scenario |

---

## 🗺️ What is going on

<div align="center"><img src="../../images/citnc_banner_06.png" width="80%"/></div></br>

---

To check if nothing broke on the last maintenance window, what we did was: compare outputs using Python dictionaries, spot differences, hope you didn't miss anything.

However, pyATS provides a much more automated way to do this: capture the device state before changes, apply the changes, capture the state after, and let the tool show you exactly what changed - meaning: no guesswork.

In this module, we turn state collection into snapshots and use structured comparison to prove changes worked. Every change becomes an auditable record that your team and compliance can trust.

**🏅 Golden rule No.2:**
> Always capture the before, prove the after, and save the evidence.

---

## 📸 Why snapshots matter

Snapshots turn vague concerns ("did anything break?") into precise evidence:

- **Before snapshot**: parsed device state captured at a point in time.
- **After snapshot**: parsed device state after your change.
- **Diff report**: side-by-side comparison showing exactly what changed, what stayed the same, and what values were affected.

This is how you prove to your team, your NOC, and compliance that a change did what it was supposed to do and broke nothing.

---

## 🔌 Step 1: Set up your environment

Reuse the virtual environment from the previous module:

```bash
cd session-02-interaction
source .venv/bin/activate
cd 02-change-validation-snapshots
```

The examples below expect the testbed inventory at:

```bash
../01-pyats-readwrite/inventory.yaml
```

---

## 📸 Step 2: Capture baseline snapshots

Before making any change, we are going to collect and save the current state of all devices, focusing on everything related to `interfaces` for now.

However, as you may have noticed in the previous lesson, processing devices one by one takes quite sometime. Given that pyATS needs to connect to each device, run the commands, and parse the results, there will always be some overhead that significantly delays the whole process.

We could use `Python multiprocessing`, however for now we will use a function from the pyATS library called `pcall`:

```python
# snapshots.py (fragment)

# pcall pairs arguments by tuple position:
# names[0] with devices[0], names[1] with devices[1], etc.
names = tuple(testbed.devices.keys())
devices = tuple(testbed.devices.values())
snapshot_dirs = tuple(snapshot_dir for _ in names)
suffixes = tuple(suffix for _ in names)

# pcall (parallel call) launches one worker per tuple position.
results = pcall(
    take_interface_snapshot, # This is our function for taking the snapshot of the devices
    device_name=names,
    device=devices,
    snapshot_dir=snapshot_dirs,
    suffix=suffixes,
)
```

A lot is going on here! Let's go line by line with the oddities:

> A **tuple** is a simple ordered group of values. We use two tuples so each device name matches its device object in the same position (first with first, second with second, and so on).

> `pcall` means **parallel call**: it runs the same function for all those pairs at the same time, so snapshots finish much faster.

> This is recommended for moderate amounts of devices. Larger amounts require `multithreading`, which is a brand new topic outside of today's scope ...

But hey, what does `take_interface_snapshot` do? Let's find out:

```python
# snapshots.py (fragment)
try:
    print(f"📸 Taking {suffix} snapshot for device {device_name} ...")

    device.connect(log_stdout=False)

    # learn("interface") executes multiple interface-related commands and
    # returns a structured object with the merged interface state.
    learned_interfaces = device.learn("interface")

    # Convert pyATS learned object to plain dict for JSON serialization.
    snapshot_data = learned_interfaces.to_dict()

    # Each device writes to its own file, so parallel writes do not collide.
    snapshot_file = snapshot_root / f"{device_name}_{suffix}.json"
    with open(snapshot_file, "w") as file_handle:
        json.dump(snapshot_data, file_handle, indent=4)

    . . .
```

Once this script is executed, we get the following output (much more faster as we are collecting the snapshots all at the same time):

```bash
📸 Taking before snapshot for device R1 ...
📸 Taking before snapshot for device R2 ...
📸 Taking before snapshot for device SW1 ...
📸 Taking before snapshot for device SW2 ...
✅ Snapshot saved: snapshots/R1_before.json
✅ Snapshot saved: snapshots/R2_before.json
✅ Snapshot saved: snapshots/SW1_before.json
✅ Snapshot saved: snapshots/SW2_before.json
```

The files have the following JSON content which has a lot of information about interfaces:

```json
{
    "context_manager": {},
    "attributes": null,
    "commands": null,
    "connections": null,
    "raw_data": false,
    "info": {
        "Loopback100": {
            "description": "Telemetry",
            "type": "Loopback",
            "oper_status": "up",
            "mtu": 1514,
            "enabled": true,
            "bandwidth": 8000000,
            "port_channel": {
                "port_channel_member": false
            },
            "delay": 5000,
            "ipv4": {
                "10.100.100.102/32": {
                    "ip": "10.100.100.102",
                    "prefix_length": "32",
                    "secondary": false
                }
            },
            "counters": {
                "in_pkts": 0,
                "in_octets": 0,
                "in_broadcast_pkts": 0,
                . . .
```

What happened is that the `.learn("interface")` function fired a series of commands related to interfaces, NOT JUST `show ip interface brief`. Afterwards, the function does a mix and match which results in these dictionaries packed with information. The best part? It is all done by pyATS itself!

> You can check which are the available snapshots and how they work [in this catalogue](https://pubhub.devnetcloud.com/media/genie-feature-browser/docs/#/models).

---

## 🔄 Step 3: Apply the changes

Make the same remediation you learned in the previous module:

```python
# apply_configs.py
LOOPBACK400_CONFIG = [
    "interface Loopback400",
    "description OOB",
    "ip address 10.220.220.223 255.255.255.255",
    "no shutdown",
]

device.configure(LOOPBACK400_CONFIG)
```

---

## 📸 Step 4: Capture post-change snapshot

Immediately after the change, capture the same state again:

```python
# snapshots.py (fragment)
post_snapshot = capture_snapshot(device, device_name=name)
post_snapshot.save(f"snapshots/{name}_after.json")
```

```bash
📸 Taking after snapshot for device R1 ...
📸 Taking after snapshot for device R2 ...
📸 Taking after snapshot for device SW1 ...
📸 Taking after snapshot for device SW2 ...
✅ Snapshot saved: snapshots/R1_after.json
✅ Snapshot saved: snapshots/R2_after.json
✅ Snapshot saved: snapshots/SW1_after.json
✅ Snapshot saved: snapshots/SW2_after.json
```

---

## 🔄 Step 5: Generate diff report

Load both snapshots and compare them side by side:

```python
# snapshots.py (fragment)
  with open(before_file) as file_handle:
      before_data = json.load(file_handle)

  with open(after_file) as file_handle:
      after_data = json.load(file_handle)

  # Genie's Diff function compares and contrasts the contents of the before and after snapshots
  genie_diff = Diff(before_data, after_data)
  genie_diff.findDiff()
```

The diff report shows that the interface `Loopback400` is brand new:

```bash
+ Loopback400:
+  bandwidth: 8000000
+  counters:
+   in_broadcast_pkts: 0
+   in_crc_errors: 0
+   in_errors: 0
+   in_multicast_pkts: 0
+   in_octets: 0
+   in_pkts: 0
+   last_clear: never
+   out_broadcast_pkts: 0
+   out_errors: 0
+   out_multicast_pkts: 0
+   out_octets: 0
+   out_pkts: 0
+   rate:
+    in_rate: 0
+    in_rate_pkts: 0
+    load_interval: 300
+    out_rate: 0
+    out_rate_pkts: 0
+  delay: 5000
+  description: OOB
+  enabled: True
+  encapsulation:
+   encapsulation: loopback
+  ipv4:
+   10.220.220.223/32:
+    ip: 10.220.220.223
+    prefix_length: 32
+    secondary: False
+  mtu: 1514
+  oper_status: up
+  port_channel:
+   port_channel_member: False
+  switchport_enable: False
+  type: Loopback
```

The diff report becomes your permanent record:

- Timestamp: when the snapshot was taken
- Device inventory: which devices were checked
- Changed fields: only the differences
- Unchanged fields: proof nothing unintended was affected

Store it alongside your change ticket or configuration management system.

---

## 🧠 Concept Mapping

| Snapshot concept | Operations equivalent |
|---|---|
| Baseline snapshot | "Show me what it looks like right now" |
| Post-change snapshot | "Show me what it looks like after the fix" |
| Diff report | Change control evidence |

---

## 🚀 What's Next

In the final lesson of this session, we move from CLI-based snapshots to live network state through APIs. You will learn API essentials, how to structure RESTCONF calls in Python, and how to validate interface state directly from IOS XE in a repeatable workflow.

That is the bridge to **Session 02: API Essentials with IOS XE RESTCONF**.
