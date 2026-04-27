# 🔧 Session 03: From Script to Tool - Python Standards for Network Automation
Topics: 🧩 Functions · ✍️ Type hints & docstrings · ⌨️ CLI with argparse

---

## 🎯 By the end of this session you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 🧩 Split a flat script into focused, single-purpose functions |
| 2 | ✍️ Add type hints so Python and your editor catch mistakes before runtime |
| 3 | 📖 Write docstrings that explain what a function does and what it expects |
| 4 | ⌨️ Accept CLI arguments with `argparse` so the script runs without code edits |
| 5 | 🏆 Combine all four into a tool any engineer can run, read, and build on |

---

## 🗺️ What is going on

<div align="center"><img src="../../images/citnc_banner_03.png" width="80%"/></div></br>

---

Alice shares `config_renderer.py` with the team. Two problems surface immediately: Bob doesn't know which files to pass as input, so he opens the script and starts editing the hardcoded paths. Poncho copies the script and hard-codes a new template name for a different project. Both changes drift from the original, and when Alice fixes a bug, nobody picks it up.

The script works, but it isn't *usable*. The fix isn't more code, it's better structure. They refactor `config_renderer.py` into a tool with clear boundaries, self-documenting functions, and a CLI interface anyone can discover with `--help`.

**🏅 Golden rule No.3:**
> Write code for the next engineer, not just for the machine.

---

## 🧩 Scripts vs Tools

A script solves a problem once. A tool solves a problem for everyone on the team, repeatably, without reading the source.

The gap between the two is smaller than it looks:

| What's missing | How to fix it |
|---|---|
| Inputs are hardcoded | Replace constants with CLI arguments (`argparse`) |
| Logic is one flat block | Split into named functions |
| No hint of what inputs expect | Add type hints |
| No explanation of what each part does | Add docstrings |

---

## 🔧 Splitting into Functions

Take the flat script from Session 02 and give each logical step its own function:

```python
def load_template(template_path: str) -> Template:
    ...

def render_configs(template: Template, inventory_path: str, output_dir: str) -> None:
    ...

def main() -> None:
    ...
```

Each function has one job. This makes the code easier to read, test, and reuse.

---

## ✍️ Type Hints and Docstrings

**Type hints** tell Python (and your editor) what kind of value a function expects and returns:

```python
def load_template(template_path: str) -> Template:
```

- `template_path: str`: the argument must be a string
- `-> Template`: the function returns a `Template` object

**Docstrings** are plain-English descriptions placed right inside the function:

```python
def load_template(template_path: str) -> Template:
    """Read the Jinja template file and return a compiled Template object."""
    with open(template_path, encoding="utf-8") as f:
        return Template(f.read())
```

---

## ⌨️ CLI Arguments with argparse

`argparse` is a Python library that turns constants into runtime arguments. Instead of editing the script to change paths, the engineer passes them at the command line:

```bash
python config_renderer.py --template ../02-howto-templates/branch-site-template-ios.j2 --inventory branch-sites.csv --output-dir ./rendered
```

The `--help` flag is generated automatically:

```bash
python config_renderer.py --help
```

```
usage: config_renderer.py [-h] --template TEMPLATE --inventory INVENTORY [--output-dir OUTPUT_DIR]

Render Cisco IOS configs from a Jinja template and a CSV inventory.

options:
  --template     Path to the .j2 template file
  --inventory    Path to the CSV inventory file
  --output-dir   Directory to save rendered configs (default: ./rendered)
```

---

## 🏆 The Complete Refactored Script

```python
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
```

Before we run it, activate the shared virtual environment from the `session-01-foundations/` folder (create it if you haven't yet — see Session 02 for instructions):

```bash
cd session-01-foundations
source .venv/bin/activate
```

Then navigate into the lesson subfolder before running the script:

```bash
cd 03-structure-scripts
```

Let's run the script with the `--help` argument to know how to use it:
```bash
python config_renderer.py --help
```

You will get the following handy documentation:
```bash
% python config_renderer.py --help
usage: config_renderer.py [-h] --template TEMPLATE --inventory INVENTORY [--output-dir OUTPUT_DIR]

Render Cisco IOS configs from a Jinja template and a CSV inventory.

options:
  -h, --help            show this help message and exit
  --template TEMPLATE   Path to the .j2 template file
  --inventory INVENTORY
                        Path to the CSV inventory file
  --output-dir OUTPUT_DIR
                        Directory to save rendered configs (default: ./rendered)
```

Now, let's run it the same way as before, but now with explicit arguments:

```bash
python config_renderer.py --template ../02-howto-templates/branch-site-template-ios.j2 --inventory ../02-howto-templates/branch-sites.csv --output-dir ./rendered
```

You will have the folder `rendered/` created, along with the `.cfg` device configuration files:
```bash
✅ Rendered config saved to ./rendered/RTR-BOS-01.cfg
✅ Rendered config saved to ./rendered/RTR-DEN-01.cfg
✅ Rendered config saved to ./rendered/RTR-MIA-01.cfg
✅ Rendered config saved to ./rendered/RTR-SEA-01.cfg
✅ Rendered config saved to ./rendered/RTR-PHX-01.cfg
```

Last but not least, if any of the parameters is wrong or missing, the tool will flag it automatically. For example, if we are missing the template path, we get the following:

```bash
python config_renderer.py --inventory branch-sites.csv --output-dir ./rendered
```

```bash
usage: config_renderer.py [-h] --template TEMPLATE --inventory INVENTORY [--output-dir OUTPUT_DIR]
config_renderer.py: error: the following arguments are required: --template
```

Now, your script is officially a tool ready to be used by other engineers.

---

## 🧠 Concept Mapping

| Python concept | Network engineering equivalent |
|---|---|
| Function | A named procedure in a runbook |
| Type hint | Input/output spec on a change request form |
| Docstring | Inline note explaining the intent of a config block |
| `argparse` argument | CLI flag on a network command (`show ip route vrf MGMT`) |
| `--help` output | Tool documentation auto-generated from the code |

---

## 🚀 What's Next

The tool now reads a CSV inventory and renders configs. CSV is convenient for small, flat datasets, but the tools engineers actually use (NetBox, SolarWinds, legacy IPAM systems) export data as **JSON** or **XML**. The moment someone hands you a file from one of those tools instead of a hand-crafted spreadsheet, the renderer breaks.

Session 04 tackles that directly: you will learn to read JSON and XML exports, understand their structure, and adapt the renderer to accept them as inventory input without touching the template or the rendering logic.

That is the bridge to **Session 04: Structured Data for Network Engineers - JSON and XML Parsing**.