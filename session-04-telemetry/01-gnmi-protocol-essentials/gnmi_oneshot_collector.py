"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 04 - Telemetry
Module: 01 - gNMI Protocol Essentials
Script: gnmi_oneshot_collector.py
"""

import os
import json
import grpc
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

from dotenv import load_dotenv
from gnmi.proto import gnmi_pb2, gnmi_pb2_grpc

"""
- gnmi_pb2:
    Contains protobuf message classes and enums (for example Path,
    CapabilityRequest, GetRequest, Encoding).

- gnmi_pb2_grpc:
    Contains gRPC client/server helpers. On the client side, we use
    gNMIStub(channel) to call RPCs like Capabilities() and Get().

Execution flow:
1) Load credentials from .env
2) Create a gRPC channel and gNMI stub
3) Call Capabilities() as a connectivity/protocol check
4) Build a GetRequest for /interfaces/interface
5) Call Get(), decode JSON_IETF payload, print pretty JSON
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

# 1. Open insecure channel

# grpc.insecure_channel() builds the transport session to the device.
# In production, prefer a secure channel with TLS certificates.
channel = grpc.insecure_channel(f"{HOST}:{PORT}")

# gnmi_pb2_grpc.gNMIStub is the RPC client generated from gnmi.proto.
# A stub is the client-side proxy object that lets your Python code call remote gNMI methods as if they were local functions
# The stub exposes methods for each gNMI RPC endpoint.
stub = gnmi_pb2_grpc.gNMIStub(channel)

# 2. Capabilities RPC: connectivity check

print("Testing gNMI connectivity...")

# gnmi_pb2.CapabilityRequest is a protobuf request message type.
# stub.Capabilities() performs the actual RPC call via gRPC.
caps = stub.Capabilities(gnmi_pb2.CapabilityRequest(), metadata=METADATA)

print(f"✅ Connected! \n\ngNMI version: {caps.gNMI_version}")
print(f"Supported encodings: {[gnmi_pb2.Encoding.Name(e) for e in caps.supported_encodings]}")
print(f"Supported models: {len(caps.supported_models)} model(s)\n")

# 3. One-shot GET: interface oper-status

PATH = "/interfaces/interface"
print(f"GET {PATH}\n")

# gnmi_pb2.GetRequest is another protobuf message type.
# We pass the path as gnmi_pb2.Path built by make_path().
request = gnmi_pb2.GetRequest(
    path=[make_path(PATH)],
    encoding=gnmi_pb2.Encoding.JSON_IETF,
)

# stub.Get() sends the gNMI Get RPC and returns a GetResponse message.
response = stub.Get(request, metadata=METADATA)

for notif in response.notification:
    for update in notif.update:
        # json_ietf_val is bytes, so we convert to Python dict for pretty output.
        raw = update.val.json_ietf_val
        val = json.loads(raw) if raw else None
        print(json.dumps(val, indent=2))

channel.close()