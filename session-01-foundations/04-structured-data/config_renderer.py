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
    with open(inventory_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            inventory.append(row)
    return inventory


def load_inventory_json(inventory_path: str) -> list[dict]:
    """Load device inventory from a JSON file."""
    with open(inventory_path, encoding="utf-8") as f:
        return json.load(f)


def load_inventory_xml(inventory_path: str) -> list[dict]:
    """Load device inventory from an XML file."""
    tree = ET.parse(inventory_path)
    inventory = []
    for device in tree.getroot().findall("device"):
        device_dict = {}
        for child in device:
            device_dict[child.tag] = child.text
        inventory.append(device_dict)
    return inventory


def load_inventory(inventory_path: str, format_type: str) -> list[dict]:
    """Load inventory based on file format."""
    loaders = {
        "csv": load_inventory_csv,
        "json": load_inventory_json,
        "xml": load_inventory_xml,
    }
    
    if format_type not in loaders:
        raise ValueError(f"Unsupported format: {format_type}. Supported: {', '.join(loaders.keys())}")
    
    return loaders[format_type](inventory_path)


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
