#!/usr/bin/env python3
"""
Minimal gNMI STREAM -> InfluxDB writer for IOS XR interface packet counters.

Collects only in_pkts and out_pkts from all interfaces.
Prints only when a point is created and its contents.
"""

import json
import os
from typing import Any, Dict, Iterable, Iterator, List, Tuple

# Keep this before importing gnmi/protobuf modules.
os.environ.setdefault("PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION", "python")

import grpc
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from gnmi.proto import gnmi_pb2, gnmi_pb2_grpc

# Reuse lesson-02 environment file.
load_dotenv("../.env")

GNMI_HOST = os.getenv("GNMI_HOST")
GNMI_PORT = os.getenv("GNMI_PORT", "57400")
GNMI_USERNAME = os.getenv("GNMI_USERNAME")
GNMI_PASSWORD = os.getenv("GNMI_PASSWORD")

# Known-good path used in lesson 02.
INTERFACE_PATH = os.getenv("GNMI_INTERFACE_PATH", "/interfaces/interface")
SAMPLE_INTERVAL_NS = int(os.getenv("GNMI_SAMPLE_INTERVAL_NS", "10000000000"))

INFLUX_URL = os.getenv("INFLUX_URL", "http://localhost:8086")
INFLUX_TOKEN = os.getenv("INFLUX_TOKEN", "telemetry-super-token")
INFLUX_ORG = os.getenv("INFLUX_ORG", "telemetry")
INFLUX_BUCKET = os.getenv("INFLUX_BUCKET", "telemetry_metrics")

TARGET_COUNTER_KEYS = {"in-pkts", "out-pkts"}
INTERFACE_ID_KEYS = ("name", "interface-id", "id")
MEASUREMENT_NAME = "iosxr_interface_counters"


def make_path(xpath: str) -> Any:
    """
    Build a gNMI Path protobuf from an XPath-like string.

    Args:
        xpath: Path string such as "/interfaces/interface/state/counters".

    Outputs:
        A populated gNMI Path protobuf object.

    Example:
        "/interfaces/interface" -> Path(elem=["interfaces", "interface"])
    """
    path = gnmi_pb2.Path()
    for elem in xpath.strip("/").split("/"):
        if elem:
            path.elem.append(gnmi_pb2.PathElem(name=elem))
    return path


def subscription_request(path: str, mode: int) -> Any:
    """
    Create a STREAM subscription request for a given gNMI path.

    Args:
        path: gNMI path to subscribe to.
        mode: Subscription mode value (must be STREAM for this script).

    Outputs:
        A SubscribeRequest protobuf ready to send to gNMI Subscribe().

    Example:
        path="/interfaces/interface", mode=STREAM -> request with SAMPLE interval.
    """
    if mode != gnmi_pb2.SubscriptionList.Mode.STREAM:
        raise ValueError("This script only supports STREAM mode")

    subscription = gnmi_pb2.Subscription(
        path=make_path(path),
        mode=gnmi_pb2.SubscriptionMode.SAMPLE,
        sample_interval=SAMPLE_INTERVAL_NS,
    )

    sub_list = gnmi_pb2.SubscriptionList(
        mode=mode,
        subscription=[subscription],
        encoding=gnmi_pb2.Encoding.JSON_IETF,
    )
    return gnmi_pb2.SubscribeRequest(subscribe=sub_list)


def request_iter(path: str, mode: int) -> Iterator[Any]:
    """
    Yield the initial gNMI subscription request for the stream RPC.

    Args:
        path: gNMI path to subscribe to.
        mode: Subscription mode value.

    Outputs:
        Iterator that yields exactly one SubscribeRequest.
    """
    yield subscription_request(path, mode)


def maybe_to_float(value: Any) -> float | None:
    """
    Convert supported numeric values to float.

    Args:
        value: Candidate value from telemetry payload.

    Outputs:
        Float for int/float/digit-only string values; otherwise None.

    Example:
        "123" -> 123.0, "1.2" -> None
    """
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value.isdigit():
        return float(value)
    return None


def normalize_metric_name(name: str) -> str:
    """
    Normalize metric names for Influx tag usage.

    Args:
        name: Raw metric name from payload.

    Outputs:
        Lowercase metric with '-' and '/' replaced by '_'.

    Example:
        "in-pkts" -> "in_pkts"
    """
    return name.replace("-", "_").replace("/", "_").lower()


def discover_interface_name(data: Any) -> str:
    """
    Recursively find an interface identifier in JSON payload data.

    Args:
        data: Nested dict/list structure decoded from JSON IETF payload.

    Outputs:
        First matching interface identifier string, or empty string if not found.

    Example:
        {"interface": {"name": "GigabitEthernet0/0/0/0"}} -> "GigabitEthernet0/0/0/0"
    """
    if isinstance(data, dict):
        for key in INTERFACE_ID_KEYS:
            value = data.get(key)
            if isinstance(value, str):
                return value
        for value in data.values():
            found = discover_interface_name(value)
            if found:
                return found
    elif isinstance(data, list):
        for item in data:
            found = discover_interface_name(item)
            if found:
                return found
    return ""


def find_interface_from_path_elems(elems: Iterable[Any]) -> str:
    """
    Extract an interface identifier from gNMI path elements and keys.

    Args:
        elems: Iterable of PathElem-like protobuf objects.

    Outputs:
        Interface identifier from keys or interface path node, else empty string.
    """

    def extract_keys(elem: Any) -> Dict[str, str]:
        """
        Return keys from a path element regardless of protobuf version format.

        Args:
            elem: A PathElem-like object with a key container.

        Outputs:
            Dictionary of key/value pairs converted to strings.
        """
        keys: Dict[str, str] = {}

        # Newer protobufs may expose key as a dict-like map.
        if hasattr(elem.key, "items"):
            for k, v in elem.key.items():
                keys[str(k)] = str(v)
            return keys

        # Older protobufs may expose key as repeated KeyValue entries.
        for item in elem.key:
            if hasattr(item, "key") and hasattr(item, "value"):
                keys[str(item.key)] = str(item.value)
            elif hasattr(item, "name") and hasattr(item, "value"):
                keys[str(item.name)] = str(item.value)

        return keys

    for elem in elems:
        elem_keys = extract_keys(elem)
        for key in INTERFACE_ID_KEYS:
            if key in elem_keys:
                return elem_keys[key]
        if elem.name == "interface" and len(elem_keys) > 0:
            first_key = next(iter(elem_keys.values()))
            if isinstance(first_key, str) and first_key:
                return first_key
    return ""


def collect_packet_counters(data: Any) -> List[Tuple[str, float]]:
    """
    Recursively collect target packet counters from payload data.

    Args:
        data: Nested dict/list telemetry payload.

    Outputs:
        List of (metric_name, value) tuples for supported counters.

    Example:
        counters={"in-pkts": 10, "out-pkts": 20} -> [("in_pkts", 10.0), ("out_pkts", 20.0)]
    """
    results: List[Tuple[str, float]] = []

    if isinstance(data, dict):
        for key, value in data.items():
            if key == "counters" and isinstance(value, dict):
                for counter_name, counter_value in value.items():
                    if counter_name in TARGET_COUNTER_KEYS:
                        numeric = maybe_to_float(counter_value)
                        if numeric is not None:
                            metric_name = normalize_metric_name(counter_name)
                            results.append((metric_name, numeric))

            results.extend(collect_packet_counters(value))

    elif isinstance(data, list):
        for item in data:
            results.extend(collect_packet_counters(item))

    return results


def write_points(
    write_api: Any,
    device: str,
    interface_name: str,
    metrics: List[Tuple[str, float]],
    timestamp_ns: int | None,
) -> None:
    """
    Create and write InfluxDB points for collected interface metrics.

    Args:
        write_api: InfluxDB write API client.
        device: Device name used as a point tag.
        interface_name: Interface name used as a point tag.
        metrics: Metric/value pairs to persist.
        timestamp_ns: Optional event timestamp in nanoseconds.

    Outputs:
        None. Writes points to InfluxDB and prints each point payload.
    """
    points = []
    for metric_name, value in metrics:
        point_info = {
            "measurement": MEASUREMENT_NAME,
            "tags": {
                "device": device,
                "interface": interface_name or "unknown",
                "metric": metric_name,
            },
            "fields": {"value": value},
            "timestamp_ns": timestamp_ns,
        }
        print(f"POINT: {point_info}")

        point = (
            Point(MEASUREMENT_NAME)
            .tag("device", device)
            .tag("interface", interface_name or "unknown")
            .tag("metric", metric_name)
            .field("value", value)
        )
        if timestamp_ns:
            point = point.time(timestamp_ns)
        points.append(point)

    if points:
        write_api.write(bucket=INFLUX_BUCKET, record=points)


def main() -> None:
    """
    Subscribe to gNMI updates and persist interface packet counters to InfluxDB.

    Args:
        None.

    Outputs:
        None. Runs until interrupted and writes collected metrics to InfluxDB.
    """
    required = [GNMI_HOST, GNMI_USERNAME, GNMI_PASSWORD]
    if not all(required):
        raise ValueError(
            "Missing gNMI credentials. Set GNMI_HOST, GNMI_USERNAME, GNMI_PASSWORD in ../.env"
        )

    metadata = [("username", GNMI_USERNAME), ("password", GNMI_PASSWORD)]

    channel = grpc.insecure_channel(f"{GNMI_HOST}:{GNMI_PORT}")
    stub = gnmi_pb2_grpc.gNMIStub(channel)

    influx_client = InfluxDBClient(url=INFLUX_URL, token=INFLUX_TOKEN, org=INFLUX_ORG)
    write_api = influx_client.write_api(write_options=SYNCHRONOUS)

    response_stream = stub.Subscribe(
        request_iter(INTERFACE_PATH, gnmi_pb2.SubscriptionList.Mode.STREAM),
        metadata=metadata,
    )

    try:
        for response in response_stream:
            if not response.update:
                continue

            device = response.update.prefix.target or GNMI_HOST
            timestamp_ns = int(response.update.timestamp) if response.update.timestamp else None

            for update in response.update.update:
                raw = update.val.json_ietf_val
                if not raw:
                    continue

                payload = json.loads(raw)

                interface_from_prefix = find_interface_from_path_elems(response.update.prefix.elem)
                interface_from_path = find_interface_from_path_elems(update.path.elem)
                interface_from_payload = discover_interface_name(payload)
                interface_name = interface_from_prefix or interface_from_path or interface_from_payload

                counter_metrics = collect_packet_counters(payload)
                if not counter_metrics:
                    continue

                write_points(write_api, device, interface_name, counter_metrics, timestamp_ns)

    except KeyboardInterrupt:
        pass
    finally:
        channel.close()
        influx_client.close()


if __name__ == "__main__":
    main()
