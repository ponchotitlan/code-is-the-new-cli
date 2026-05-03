# 🏠 Session 04 Telemetry: Homework Assignment
Topics: 📡 gNMI STREAM subscriptions · 🧠 CPU telemetry collection · 🐍 Python collector fundamentals

---

In Session 04 you learned how to collect telemetry with gNMI using Python.

Now it is your turn to build your own minimal collector.

## 📋 Scenario

Use the same IOS XR sandbox device from Lesson 01 and create a Python script that subscribes via gNMI STREAM to CPU telemetry every 10 seconds.

The goal is to practice the full telemetry flow:

1. Connect to IOS XR using gNMI.
2. Create a STREAM subscription in SAMPLE mode.
3. Receive CPU updates every 10 seconds.
4. Parse and print readable output.

---

## 1. Environment Setup

Reuse your Session 04 environment:

```bash
cd session-04-telemetry
source .venv/bin/activate
pip install -r requirements.txt
```

Make sure your .env file in session-04-telemetry has:

- GNMI_HOST
- GNMI_PORT
- GNMI_USERNAME
- GNMI_PASSWORD

---

## 2. Build the Python Collector

Create this file:

- session-04-telemetry/homework/gnmi_cpu_stream_collector.py

Your script must:

1. Load credentials from .env.
2. Build a gNMI stub and authenticate with metadata username/password.
3. Create a STREAM subscription with SAMPLE mode and 10-second interval.
4. Subscribe to a CPU telemetry path.
5. Parse JSON_IETF payloads.
6. Print compact CPU telemetry lines until Ctrl+C.

Use this default CPU path first:

- /Cisco-IOS-XR-wdsysmon-fd-oper:system-monitoring/cpu-utilization

If your sandbox returns no data for that path, document in your report the path that worked for your device.

---

## 3. Script Quality Requirements

The script must include:

- At least 4 named functions.
- Type hints on all function signatures.
- Docstring on each function.
- A main entry point with if __name__ == "__main__".
- Basic error handling with try/except for connection and runtime errors.
- Graceful stop message on Ctrl+C.

---

## 4. What to Show as Output

During execution, print one concise line per update, for example:

```text
2026-05-03T14:22:10Z | device=sandbox-iosxr-1.cisco.com | cpu_total=13.2
```

If the payload has multiple CPU values, print the most relevant one and clearly label it.

---

## 5. Required Run Command

From session-04-telemetry/homework:

```bash
python gnmi_cpu_stream_collector.py
```

Let it run for at least 30 seconds and capture output.

---

## 6. Homework Report

Create:

- session-04-telemetry/homework/HW_REPORT.md

Include:

1. Sandbox URL used and test date/time.
2. CPU path attempted and final working path.
3. A short snippet of collector output.
4. One paragraph: what was the hardest part and how you solved it.

---

## 📬 Submission to this Course Repository

Inside this folder, create:

- submission-<your-github-username>.md

Use this format:

```markdown
# Homework Submission: Session 04 Telemetry

**GitHub username:** <your-username>
**Homework repository:** <link-to-your-repo>
**Sandbox used:** <IOS XR Always-On URL>
**Collector file:** gnmi_cpu_stream_collector.py
**CPU path used:** <final path>
**Most challenging part:** <one sentence>
```

Then open a PR to this repository with title:

- hw(session-04): submission from <your-github-username>

---

## ✅ Checklist Before Submitting

| # | Item |
|:---:|:---|
| 1 | gnmi_cpu_stream_collector.py exists in session-04-telemetry/homework |
| 2 | Uses STREAM + SAMPLE with 10-second interval |
| 3 | Reads credentials from .env |
| 4 | Parses and prints CPU telemetry from JSON_IETF payload |
| 5 | Includes functions, type hints, docstrings, and main() |
| 6 | Handles Ctrl+C gracefully |
| 7 | HW_REPORT.md includes path used and output evidence |
| 8 | submission-<username>.md created and PR opened |

---

## 🧠 Hints

- Start from session-04-telemetry/02-gnmi-collector/gnmi_stream_collector.py and adapt it.
- Keep output simple and readable.
- If you receive empty updates, validate the path and keep JSON_IETF enabled.
- Do not over-engineer: this homework is intentionally minimal.
