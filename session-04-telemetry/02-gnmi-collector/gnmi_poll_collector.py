"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 04 - Telemetry
Module: 02 - gNMI Collector
Script: gnmi_poll_collector.py
"""

import os
import json
import time
import grpc
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

from dotenv import load_dotenv
from gnmi.proto import gnmi_pb2, gnmi_pb2_grpc

"""
- gnmi_pb2:
    Contains protobuf message classes and enums (for example Path,
    SubscribeRequest, Subscription, SubscriptionList, Encoding).

- gnmi_pb2_grpc:
    Contains gRPC client/server helpers. On the client side, we use
    gNMIStub(channel) to call RPCs like Subscribe().

Execution flow:
1) Load credentials from .env
2) Create a gRPC channel and gNMI stub
3) Build a POLL subscription for /interfaces/interface
4) Periodically send poll triggers and decode JSON_IETF updates
"""

load_dotenv("../.env")

HOST = os.getenv("GNMI_HOST")
PORT = os.getenv("GNMI_PORT")
USERNAME = os.getenv("GNMI_USERNAME")
PASSWORD = os.getenv("GNMI_PASSWORD")

METADATA = [("username", USERNAME), ("password", PASSWORD)]

def make_path(xpath: str):
    """Convert an XPath-like string into a gNMI Path proto.

    Example:
        input  -> "/interfaces/interface/state/oper-status"
        output -> Path(elem=[
            PathElem(name="interfaces"),
            PathElem(name="interface"),
            PathElem(name="state"),
            PathElem(name="oper-status"),
        ])
    """
    path = gnmi_pb2.Path()
    for elem in xpath.strip("/").split("/"):
        path.elem.append(gnmi_pb2.PathElem(name=elem))
    return path

def request_iter(first_request, poll_interval_seconds: int = 10):
    """Yield initial POLL subscription request, then periodic poll triggers.

    Why this is needed:
    gNMI Subscribe uses a client-streaming request channel. In POLL mode, the
    client sends one initial `subscribe` request and then sends `poll` messages
    whenever it wants a fresh snapshot from the device.
    """
    yield first_request
    while True:
        time.sleep(poll_interval_seconds)
        yield gnmi_pb2.SubscribeRequest(poll=gnmi_pb2.Poll())

# 1. Open insecure channel

# grpc.insecure_channel() builds the transport session to the device.
# In production, prefer a secure channel with TLS certificates.
channel = grpc.insecure_channel(f"{HOST}:{PORT}")

# gnmi_pb2_grpc.gNMIStub is the RPC client generated from gnmi.proto.
# A stub is the client-side proxy object that lets your Python code call remote gNMI methods as if they were local functions
# The stub exposes methods for each gNMI RPC endpoint.
stub = gnmi_pb2_grpc.gNMIStub(channel)

# 2. POLL subscription: interfaces path

PATH = "/interfaces/interface"
POLL_INTERVAL_SECONDS = 10
print(f"Starting POLL subscription for {PATH} (every {POLL_INTERVAL_SECONDS}s)\n")

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
    request_iter(request, POLL_INTERVAL_SECONDS),
    metadata=METADATA,
)

try:
    for response in response_stream:
        if not response.update:
            continue
        for update in response.update.update:
            # json_ietf_val is bytes, so we convert to Python dict for pretty output.
            raw = update.val.json_ietf_val
            val = json.loads(raw) if raw else None
            print(json.dumps(val, indent=2))
except KeyboardInterrupt:
    print("\nStopping subscription...")

channel.close()