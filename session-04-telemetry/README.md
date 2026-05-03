# 📡 Session 04: Telemetry and Streaming Visibility
Topics: 🛰️ gNMI fundamentals · 📈 Telemetry subscription models · 🧪 Python collectors · 💾 InfluxDB persistence

---

## 🎯 By the end of this session you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 🛰️ Explain gNMI architecture, RPC flow, and why model-based streaming improves network observability |
| 2 | 📥 Build one-shot and continuous telemetry collectors in Python using gnmi-py |
| 3 | 🔁 Compare ONCE, POLL, and STREAM collection approaches and choose the right mode for each use case |
| 4 | 🧱 Parse and normalize telemetry updates into structured measurements ready for storage and analysis |
| 5 | 💾 Persist telemetry data into InfluxDB for historical queries, trending, and operational insights |

---

## 🗺️ What is going on

> Move from periodic scraping to model-driven streaming so your automation reacts to state changes in near real time.

---

## 📚 Session Overview

| Part | Folder | What we will look at |
|---|---|---|
| 01 | [01-gnmi-protocol-essentials](./01-gnmi-protocol-essentials) | gNMI protocol essentials, capability exchange, path modeling, and one-shot telemetry collection workflows |
| 02 | [02-gnmi-collector](./02-gnmi-collector) | Building polling and stream collectors in Python, handling updates, and structuring telemetry payloads for automation |
| 03 | [03-telemetry-persistence](./03-telemetry-persistence) | Persisting streaming telemetry to InfluxDB with Docker Compose, transforming messages, and validating stored metrics |
