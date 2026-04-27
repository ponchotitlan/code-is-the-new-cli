"""Course script metadata.

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
    inventory = []
    print("\n📂 Loading inventory from CSV file...\n")
    with open(inventory_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            inventory.append(row)
    return inventory


def load_inventory_json(inventory_path: str) -> list[dict]:
    """Load device inventory from a JSON file."""
    print("\n📂 Loading inventory from JSON file...\n")
    with open(inventory_path, encoding="utf-8") as f:
        return json.load(f)


def load_inventory_xml(inventory_path: str) -> list[dict]:
    """Load device inventory from an XML file."""
    print("\n📂 Loading inventory from XML file...\n")
    tree = ET.parse(inventory_path)                             # Parse the XML file into an ElementTree
    inventory = []                                              # Initialize empty list to store device dictionaries
    for device in tree.getroot().findall("device"):             # Find all <device> elements in the root
        device_dict = {}                                        # Create an empty dictionary for each device
        for child in device:                                    # Iterate over all child elements (fields) of the device
            device_dict[child.tag] = child.text                 # Map XML tag name to its text content
        inventory.append(device_dict)                           # Add the device dictionary to the inventory list
    return inventory                                            # Return the complete list of device dictionaries


def load_inventory(inventory_path: str, format_type: str) -> list[dict]:
    """Load inventory based on file format."""
    if format_type == "csv":
        return load_inventory_csv(inventory_path)
    elif format_type == "json":
        return load_inventory_json(inventory_path)
    elif format_type == "xml":
        return load_inventory_xml(inventory_path)


def render_configs(template: Template, inventory: list[dict], output_dir: str) -> None:
    """Render one config file per device in the inventory.

    Output files are named <BRANCH_HOSTNAME>.cfg and saved to output_dir.
    """
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
        default="csv",
        choices=["csv", "json", "xml"],
        help="Inventory file format (default: csv)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="rendered",
        help="Directory to save rendered configs (default: ./rendered)",
    )
    args = parser.parse_args()

    template = load_template(args.template)
    inventory = load_inventory(args.inventory, args.format)
    render_configs(template, inventory, args.output_dir)


if __name__ == "__main__":
    main()
