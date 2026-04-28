"""
Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 01 - Foundations
Module: 03 - Structure Scripts
Script: config_renderer.py
"""

import argparse
import csv
import os

from jinja2 import Template


def load_template(template_path: str) -> Template:
    """Read the Jinja template file and return a compiled Template object."""
    with open(template_path, encoding="utf-8") as f:
        return Template(f.read())


def render_configs(template: Template, inventory_path: str, output_dir: str) -> None:
    """Render one config file per device row in the CSV inventory.

    Output files are named <BRANCH_HOSTNAME>.cfg and saved to output_dir.
    """
    os.makedirs(output_dir, exist_ok=True)

    with open(inventory_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            output_path = os.path.join(output_dir, f"{row['BRANCH_HOSTNAME']}.cfg")
            with open(output_path, "w", encoding="utf-8") as out:
                out.write(template.render(**row))
            print(f"✅ Rendered config saved to {output_path}")


def main() -> None:
    """Parse CLI arguments and run the config renderer."""
    parser = argparse.ArgumentParser(
        description="Render Cisco IOS configs from a Jinja template and a CSV inventory."
    )
    parser.add_argument(
        "--template", type=str, required=True, help="Path to the .j2 template file"
    )
    parser.add_argument(
        "--inventory", type=str, required=True, help="Path to the CSV inventory file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="rendered",
        help="Directory to save rendered configs (default: ./rendered)",
    )
    args = parser.parse_args()

    template = load_template(args.template)
    render_configs(template, args.inventory, args.output_dir)


if __name__ == "__main__":
    main()