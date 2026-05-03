# 📡 Session 04 | Lesson 02: Building a gNMI Collector
Topics: 🐍 Python gNMI client · 🔄 Subscription handling · 📊 Message parsing

---

## 🎯 By the end of this lesson you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 🔌 Connect to a gNMI device using the gnmi-py library and dial-in subscriptions |
| 2 | 🔄 Create and manage STREAM, ONCE, and POLL subscriptions with proper encoding |
| 3 | 📥 Handle asynchronous push updates from a gNMI stream and validate message structure |
| 4 | 🧠 Parse gNMI JSON updates into structured Python objects for processing |
| 5 | 🛡️ Implement graceful shutdown, error handling, and connection recovery logic |

---

## 🗺️ What is going on

<div align="center"><img src="../../images/citnc_banner_13.png" width="80%"/></div></br>

---

A gNMI device is useless without a collector: the Python script that connects, subscribes, and processes streams. In this lesson, you'll write your first gNMI collector using the gnmi-py library, handling real-time updates asynchronously, and parsing them into actionable data structures.

**🏅 Golden rule:**
> Adjust your collector to the subscription mode that fits your use case the best.

---

## 🗂️ Today's lab

For this lesson, we will reuse the [IOS XR Always-on](https://devnetsandbox.cisco.com/DevNet/catalog/iosxr-always-on-public_iosxr-always-on-public) device from the last lesson.

Likewise, we will reuse the same environment variables, so make sure to have a `.env` file populated with the credentials of your Sandbox device in the `session-04-telemetry/` directory.

### Virtual Environment

Finally, we will reuse as well the Virtual Environment, so go ahead and activate it for this lesson:

```bash
cd session-04-telemetry/
source .venv/bin/activate
cd 02-gnmi-collector/
```

---

## 🚿 `STREAM` subscription 

The following script is based on the example from the previous lesson. But this time, we will be subscribing to updates of `interfaces` statuses, which will be sent to us **every 10 seconds**.

The collector exits only when we press Ctrl + C.

The main changes are the following:

```python
# gnmi_stream_collector

# Configure one subscription in SAMPLE mode under a STREAM subscription list.
# sample_interval is in nanoseconds (10s = 10_000_000_000).
subscription = gnmi_pb2.Subscription(
    path=make_path(PATH),
    mode=gnmi_pb2.SubscriptionMode.SAMPLE,
    sample_interval=10_000_000_000,
)

sub_list = gnmi_pb2.SubscriptionList(
    mode=gnmi_pb2.SubscriptionList.Mode.STREAM,
    subscription=[subscription],
    encoding=gnmi_pb2.Encoding.JSON_IETF,
)

# Subscribe RPC expects an iterator of SubscribeRequest messages.
request = gnmi_pb2.SubscribeRequest(subscribe=sub_list)
response_stream = stub.Subscribe(request_iter(), metadata=METADATA)
```

The following diagram explains the flow of this script:

```text
┌────────────────────────────────────────┐      ┌────────────────────────────────────────┐
│ 💻 Python Collector                    │      │ 🖥️ gNMI Device                         │
│ (gnmi_stream_collector.py)             │      │ (IOS XR Sandbox)                       │
└────────────────────────────────────────┘      └────────────────────────────────────────┘
                │                                                │
                │ 1) 🔐 Load .env credentials                    │
                │    + build metadata                            │
                │                                                │
                │ 2) 🔌 Create gRPC channel + gNMI stub          │
                │                                                │
                │ 3) 📦 Build STREAM subscription                │
                │    path=/interfaces/interface                  │
                │    mode=SAMPLE, interval=10s                   │
                │                                                │
                │ 4) 📤 SubscribeRequest                         │
                ├───────────────────────────────────────────────▶│
                │                                                │
                │                                                │ 5) ✅ Accept subscription
                │                                                │    and start telemetry stream
                │ ◀──────────────────────────────────────────────┤
                │ 6) 📥 SubscribeResponse update #1              │
                │ ◀──────────────────────────────────────────────┤
                │ 7) 📥 SubscribeResponse update #2              │
                │ ◀──────────────────────────────────────────────┤
                │ 8) 📥 ...continues every 10s                   │
                │                                                │
                │ 9) 🧠 Decode json_ietf_val + print JSON        │
                │                                                │
                │ 10) 🛑 Ctrl+C                                  │
                │                                                │
                │ 11) 🧹 channel.close()                         │
                ▼                                                ▼
            Stream ends cleanly                          Server stream ends
```

Basically, we get the same JSON information that we got in the previous lesson, but on regular intervals of 10 seconds!

---

## 🗳️ `POLL` subscription 

`POLL` is still a gNMI `Subscribe` session, but the device does **not** push updates on its own interval.
Instead, the collector explicitly asks for data each time it wants a fresh snapshot.

Think of it like this:
- 🚿 `STREAM`: "send me updates continuously"
- 🗳️ `POLL`: "send me updates **when I ask**"

The following code snippet shows how to setup this subscription mode.

```python
# gnmi_poll_collector.py
PATH = "/interfaces/interface"
POLL_INTERVAL_SECONDS = 10

# Configure a POLL subscription list. The device returns data when poll
# messages are sent by the client.
subscription = gnmi_pb2.Subscription(
    path=make_path(PATH),
)

sub_list = gnmi_pb2.SubscriptionList(
    mode=gnmi_pb2.SubscriptionList.Mode.POLL,
    subscription=[subscription],
    encoding=gnmi_pb2.Encoding.JSON_IETF,
)

# Subscribe RPC expects an iterator of SubscribeRequest messages.
request = gnmi_pb2.SubscribeRequest(subscribe=sub_list)

response_stream = stub.Subscribe(
    request_iter(request, POLL_INTERVAL_SECONDS), metadata=METADATA,
)
```

> We are simulating the demand for data using the counter `POLL_INTERVAL_SECONDS`

The following diagram explains the workflow of this collector type:

```text
┌────────────────────────────────────────┐      ┌────────────────────────────────────────┐
│ 💻 Python Collector                    │      │ 🖥️ gNMI Device                         │
│ (gnmi_poll_collector.py)               │      │ (IOS XR Sandbox)                       │
└────────────────────────────────────────┘      └────────────────────────────────────────┘
                │                                                │
                │ 1) 🔐 Load .env credentials                    │
                │    + build metadata                            │
                │                                                │
                │ 2) 🔌 Create gRPC channel + gNMI stub          │
                │                                                │
                │ 3) 📦 Build POLL subscription                  │
                │    path=/interfaces/interface                  │
                │    mode=POLL (no interval set by device)       │
                │                                                │
                │ 4) 📤 SubscribeRequest (subscribe=sub_list)    │
                ├───────────────────────────────────────────────▶│
                │                                                │
                │                                                │ 5) ✅ Accept subscription
                │                                                │    (waits for poll triggers)
                │                                                │
                │ 6) 📤 SubscribeRequest(poll=Poll())  ← t=0s    │
                ├───────────────────────────────────────────────▶│
                │ ◀──────────────────────────────────────────────┤
                │ 7) 📥 SubscribeResponse snapshot #1            │
                │    🧠 Decode json_ietf_val + print JSON        │
                │                                                │
                │    ⏳ wait 10s...                              │
                │                                                │
                │ 8) 📤 SubscribeRequest(poll=Poll())  ← t=10s   │
                ├───────────────────────────────────────────────▶│
                │ ◀──────────────────────────────────────────────┤
                │ 9) 📥 SubscribeResponse snapshot #2            │
                │    🧠 Decode json_ietf_val + print JSON        │
                │                                                │
                │    ⏳ ...repeats every 10s                     │
                │                                                │
                │ 10) 🛑 Ctrl+C                                  │
                │                                                │
                │ 11) 🧹 channel.close()                         │
                ▼                                                ▼
            Poll loop ends                           Server session ends
```

---

## 🔍 `POLL` vs `STREAM` vs Single-Shot

| Aspect | 🚿 `STREAM` | 🗳️ `POLL` | 📸 Single-shot `GET` |
|---|---|---|---|
| Who decides when updates arrive? | Device (based on sample/on-change config) | Collector (when it sends poll trigger) | Collector (one request, then done) |
| Traffic pattern | Continuous flow | Burst per poll request | Single request/response |
| Best for | Near-real-time dashboards/alerts | On-demand snapshots and controlled collection | One-time state checks, scripts, debugging |
| Client behavior | Mostly receive loop | Send trigger + receive response loop | Send request, read response, disconnect |
| Session stays open? | ✅ Yes (until Ctrl+C) | ✅ Yes (until Ctrl+C) | ❌ No (closes after response) |

Rule of thumb:
- Choose `STREAM` when you need continuous observability.
- Choose `POLL` when you need tighter control over request timing and data volume.
- Choose a single-shot `GET` when you just need a quick one-time read with no ongoing session.

