"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 01 - Foundations
Module: 04 - Structured Data
Script: config_renderer.py
"""

import argparse
import csv
import json
import os
import xml.etree.ElementTree as ET

from jinja2 import Template


def load_template(template_path: str) -> Template:
    """Read the Jinja template file and return a compiled Template object."""
    with open(template_path, encoding="utf-8") as f:
        return Template(f.read())


def load_inventory_csv(inventory_path: str) -> list[dict]:
    """Load device inventory from a CSV file."""
    print("\n📂 Loading inventory from CSV file...\n")
    inventory = []

    with open(inventory_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            inventory.append(row)

    return inventory


def load_inventory_json(inventory_path: str) -> list[dict]:
    """Load device inventory from a JSON file."""
    print("\n📂 Loading inventory from JSON file...\n")
    with open(inventory_path, encoding="utf-8") as f:
        inventory = json.load(f)
        print(inventory)
        return inventory


def load_inventory_xml(inventory_path: str) -> list[dict]:
    """Load device inventory from an XML file."""
    print("\n📂 Loading inventory from XML file...\n")

    # Parse the XML file and collect each <device> as a dictionary.
    tree = ET.parse(inventory_path)
    root = tree.getroot()
    inventory = []

    for device_element in root.findall("device"):
        device_data = {}

        # Every child element becomes one key/value pair in the device record.
        for field in device_element:
            device_data[field.tag] = field.text

        inventory.append(device_data)

    print(inventory)
    return inventory


def load_inventory(inventory_path: str, format_type: str) -> list[dict]:
    """Load inventory based on file format."""
    if format_type == "csv":
        return load_inventory_csv(inventory_path)

    if format_type == "json":
        return load_inventory_json(inventory_path)

    if format_type == "xml":
        return load_inventory_xml(inventory_path)


def detect_inventory_format(inventory_path: str) -> str:
    """Infer inventory format from file extension."""
    if inventory_path.lower().endswith(".csv"):
        return "csv"

    if inventory_path.lower().endswith(".json"):
        return "json"

    if inventory_path.lower().endswith(".xml"):
        return "xml"


def render_configs(template: Template, inventory: list[dict], output_dir: str) -> None:
    """Render one config file per device in the inventory.

    Output files are named <BRANCH_HOSTNAME>.cfg and saved to output_dir.
    """
    print(f"\n📝 Step 3/3: Rendering {len(inventory)} device configuration files...\n")
    os.makedirs(output_dir, exist_ok=True)

    for device in inventory:
        output_path = os.path.join(output_dir, f"{device['BRANCH_HOSTNAME']}.cfg")
        with open(output_path, "w", encoding="utf-8") as out:
            out.write(template.render(**device))
        print(f"✅ Rendered config saved to {output_path}")


def main() -> None:
    """Parse CLI arguments and run the config renderer."""
    parser = argparse.ArgumentParser(
        description="Render Cisco IOS configs from a Jinja template and an inventory (CSV, JSON, or XML)."
    )
    parser.add_argument(
        "--template", type=str, required=True, help="Path to the .j2 template file"
    )
    parser.add_argument(
        "--inventory", type=str, required=True, help="Path to the inventory file (CSV, JSON, or XML)"
    )
    parser.add_argument(
        "--format",
        type=str,
        default="auto",
        choices=["auto", "csv", "json", "xml"],
        help="Inventory file format (default: auto-detect from extension)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="rendered",
        help="Directory to save rendered configs (default: ./rendered)",
    )
    args = parser.parse_args()

    print("\n🚀 Starting configuration rendering workflow...\n")

    if args.format == "auto":
        selected_format = detect_inventory_format(args.inventory)
        print(f"🔎 Inventory format detected automatically: {selected_format}")
    else:
        selected_format = args.format
        print(f"🧭 Inventory format selected manually: {selected_format}")

    print(f"\n📄 Step 1/3: Loading template from: {args.template}")
    template = load_template(args.template)

    print(f"📂 Step 2/3: Loading inventory from: {args.inventory}")
    inventory = load_inventory(args.inventory, selected_format)

    render_configs(template, inventory, args.output_dir)

    print("\n🎉 Workflow complete.")
    print(f"✅ Total rendered files: {len(inventory)}")
    print(f"📁 Output directory: {args.output_dir}\n")


if __name__ == "__main__":
    main()
