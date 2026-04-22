"""Take pyATS interface snapshots and compare them with Genie Diff.

Modes:
  - pre-snapshot:  collect interface snapshots and save as *_before.json
  - post-snapshot: collect interface snapshots and save as *_after.json
  - report-diff:   compare two JSON files using Genie Diff
"""

import argparse
import json
from pathlib import Path
from typing import Any

from genie.utils.diff import Diff
from pyats.async_ import pcall
from pyats.topology import loader


def to_json_safe(value: Any) -> Any:
    """Convert complex objects into JSON-serializable structures.

    Args:
        value: Any Python object, including Genie Diff custom objects.

    Returns:
        A JSON-safe representation built from dict/list/primitive values.
    """
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple, set)):
        return [to_json_safe(item) for item in value]

    if hasattr(value, "to_dict"):
        try:
            return to_json_safe(value.to_dict())
        except Exception:
            pass

    if hasattr(value, "__dict__"):
        try:
            return to_json_safe(vars(value))
        except Exception:
            pass

    # Fallback for objects such as Genie ModifiedItem.
    return str(value)


def take_interface_snapshot( device_name: str, device: Any, snapshot_dir: str, suffix: str) -> dict[str, Any]:
    """Capture and store interface learned state for one device.

    This function is executed in parallel by pyATS ``pcall``, once per device.

    Args:
        device_name: Name of the device from the testbed inventory.
        device: pyATS device object used to connect and learn interface state.
        snapshot_dir: Directory where snapshot files are saved.
        suffix: Filename suffix, either ``before`` or ``after``.

    Returns:
        A dictionary with worker status for logging and summary output.
    """
    snapshot_root = Path(snapshot_dir)
    snapshot_root.mkdir(exist_ok=True)

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

        return {"device": device_name, "ok": True, "file": str(snapshot_file)}
    except Exception as error:
        return {"device": device_name, "ok": False, "error": str(error)}
    finally:
        try:
            # Always disconnect, even when a device fails, so sessions are not leaked.
            device.disconnect()
        except Exception:
            pass


def run_snapshot_mode(testbed_file: str, snapshot_dir: str, suffix: str) -> None:
    """Run pre/post snapshot collection in parallel for all devices.

    Args:
        testbed_file: Path to the pyATS testbed inventory YAML file.
        snapshot_dir: Directory where snapshot JSON files are saved.
        suffix: Filename suffix applied to each snapshot, either ``before`` or ``after``.
    """
    testbed = loader.load(testbed_file)

    # pcall pairs arguments by tuple position:
    # names[0] with devices[0], names[1] with devices[1], etc.
    names = tuple(testbed.devices.keys())
    devices = tuple(testbed.devices.values())
    snapshot_dirs = tuple(snapshot_dir for _ in names)
    suffixes = tuple(suffix for _ in names)

    # pcall (parallel call) launches one worker per tuple position.
    results = pcall(
        take_interface_snapshot,
        device_name=names,
        device=devices,
        snapshot_dir=snapshot_dirs,
        suffix=suffixes,
    )

    for result in results:
        if result.get("ok"):
            print(f"✅ Snapshot saved: {result['file']}")
        else:
            print(f"❌ Failed snapshot on {result['device']}: {result['error']}")


def run_diff_mode(before_file: str, after_file: str, output_file: str | None) -> None:
    """Compare two snapshot JSON files using Genie Diff.

    Args:
        before_file: Path to the baseline snapshot JSON (typically ``*_before.json``).
        after_file: Path to the post-change snapshot JSON (typically ``*_after.json``).
        output_file: Optional path to save the diff output as JSON. If ``None``,
            the diff is printed to the terminal instead.
    """
    with open(before_file) as file_handle:
        before_data = json.load(file_handle)

    with open(after_file) as file_handle:
        after_data = json.load(file_handle)

    genie_diff = Diff(before_data, after_data)
    genie_diff.findDiff()

    if output_file:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as file_handle:
            file_handle.write(str(genie_diff))
        print(f"📄 Diff report saved to: {output_path}")
    else:
        print("🔎 Differences found:")
        print(genie_diff)


def build_parser() -> argparse.ArgumentParser:
    """Build CLI parser for snapshot and diff operations.

    Returns:
        Configured ``ArgumentParser`` with ``pre-snapshot``, ``post-snapshot``,
        and ``report-diff`` subcommands.
    """
    parser = argparse.ArgumentParser(
        description="Take pyATS snapshots and compare them with Genie Diff.",
    )
    subparsers = parser.add_subparsers(dest="mode", required=True)

    pre_parser = subparsers.add_parser(
        "pre-snapshot",
        help="Collect interface snapshots and save them with *_before.json suffix.",
    )
    pre_parser.add_argument(
        "--testbed-file",
        default="../01-pyats-readwrite/inventory.yaml",
        help="Path to pyATS testbed inventory file.",
    )
    pre_parser.add_argument(
        "--snapshot-dir",
        default="snapshots",
        help="Directory where snapshot JSON files are saved.",
    )

    post_parser = subparsers.add_parser(
        "post-snapshot",
        help="Collect interface snapshots and save them with *_after.json suffix.",
    )
    post_parser.add_argument(
        "--testbed-file",
        default="../01-pyats-readwrite/inventory.yaml",
        help="Path to pyATS testbed inventory file.",
    )
    post_parser.add_argument(
        "--snapshot-dir",
        default="snapshots",
        help="Directory where snapshot JSON files are saved.",
    )

    diff_parser = subparsers.add_parser(
        "report-diff",
        help="Compare two snapshot JSON files using Genie Diff.",
    )
    diff_parser.add_argument(
        "--before-file",
        required=True,
        help="Path to baseline snapshot JSON (typically *_before.json).",
    )
    diff_parser.add_argument(
        "--after-file",
        required=True,
        help="Path to post-change snapshot JSON (typically *_after.json).",
    )
    diff_parser.add_argument(
        "--output-file",
        help="Optional path to save diff JSON output. If omitted, prints to terminal.",
    )

    return parser


def main() -> None:
    """Parse CLI arguments and dispatch to the requested mode.

    Reads the ``mode`` subcommand from the parsed arguments and calls
    ``run_snapshot_mode`` or ``run_diff_mode`` accordingly.
    """
    parser = build_parser()
    args = parser.parse_args()

    if args.mode == "pre-snapshot":
        run_snapshot_mode(args.testbed_file, args.snapshot_dir, suffix="before")
    elif args.mode == "post-snapshot":
        run_snapshot_mode(args.testbed_file, args.snapshot_dir, suffix="after")
    elif args.mode == "report-diff":
        run_diff_mode(args.before_file, args.after_file, args.output_file)


if __name__ == "__main__":
    main()
