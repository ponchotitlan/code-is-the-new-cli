"""Course script metadata.

Course: Code Is The New CLI - by Cisco DevNet X Nairobi Devops Community
Author: Alfonso (Poncho) Sandoval - alfsando@cisco.com
Session: Session 01 - Foundations
Module: 02 - Howto Templates
Script: config_renderer.py
"""

# --- Imports: bring in the tools we need ---
import csv
from pathlib import Path
from jinja2 import Template

# --- Inputs: edit these paths if you move the files ---
TEMPLATE_PATH = Path("branch-site-template-ios.j2")
INVENTORY_PATH = Path("branch-sites.csv")

# --- Load the template once, reuse it for every device ---
template = Template(TEMPLATE_PATH.read_text(encoding="utf-8"))

# --- Loop: one rendered config file per row in the CSV ---
with INVENTORY_PATH.open(encoding="utf-8") as f:
    for row in csv.DictReader(f):
        output_path = Path(f"{row['BRANCH_HOSTNAME']}.cfg")
        output_path.write_text(template.render(**row), encoding="utf-8")
        print(f"✅ Rendered config saved to {output_path}")