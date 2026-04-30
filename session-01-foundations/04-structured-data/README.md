# 📦 Session 01 | Lesson 04: Structured Data for Network Engineers - JSON and XML Parsing
Topics: 📄 JSON · 🌐 XML · 🔍 Parsing · 🔧 Adapting tools

---

## 🎯 By the end of this session you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 📄 Read and understand JSON exports produced by modern IPAM and CMDB tools |
| 2 | 🌐 Navigate XML exports from legacy network management tools and reports |
| 3 | 🔍 Identify the few fields required to render branch configurations |
| 4 | ▶️ Run `config_renderer.py` with JSON or XML inventory files with minimal CLI options |
| 5 | ⚖️ Choose the right format for the job based on the data source |

---

## 🗺️ What is going on

<div align="center"><img src="../../images/citnc_banner_04.png" width="80%"/></div></br>

---

The renderer works perfectly, as long as the inventory is a CSV. Then the team migrates to NetBox as their IPAM tool. Ops exports the branch site inventory directly from the NetBox UI and drops a JSON file in the shared drive. Bob finds an older XML export from the legacy IPAM tool that was replaced two years ago and never migrated; it still has the most complete record of the WAN addressing scheme. Poncho downloads a NetBox report for a third site, also XML.

The data is all there. The template is ready. The tool breaks on every single file.

The problem isn't the renderer: it's that the team assumed the world speaks CSV. Before touching the code, they need to learn how to *read* the formats their tools actually produce.

**🏅 Golden rule No.4:**
> Understand your data before you write the code that reads it.

---

## 📄 Why JSON?

JSON (JavaScript Object Notation) is the default format for REST APIs. It maps directly to Python dictionaries and lists, which makes it easy to work with using the built-in `json` module.

A branch site entry that was a CSV row now looks like this:

```json
{
  "BRANCH_HOSTNAME": "RTR-BOS-01",
  "BRANCH_IP": "10.0.1.1",
  "BRANCH_SUBNET": "255.255.255.0",
  "WAN_IP": "203.0.113.1"
}
```

For this session, the key point is practical: if the file contains the same fields as CSV (`BRANCH_HOSTNAME`, `BRANCH_IP`, `BRANCH_SUBNET`, `WAN_IP`), the renderer can use it directly.

---

## 🌐 Why XML?

XML (eXtensible Markup Language) is the format behind **NETCONF** and many older vendor APIs. It is more verbose than JSON, but it carries structure, namespaces, and ordering that matter for network configuration.

The same branch site in XML:

```xml
<device>
  <BRANCH_HOSTNAME>RTR-BOS-01</BRANCH_HOSTNAME>
  <BRANCH_IP>10.0.1.1</BRANCH_IP>
  <BRANCH_SUBNET>255.255.255.0</BRANCH_SUBNET>
  <WAN_IP>203.0.113.1</WAN_IP>
</device>
```

For this session, do not over-focus on Python parsing details. Focus on structure: each `<device>` block should include the same fields expected by the template.

---

## 🧩 Supporting many data formats

For this session, treat the tool as a black box with 3 simple inputs:

1. Template file (`.j2`)
2. Inventory file (`.csv`, `.json`, or `.xml`)
3. Output folder (`./rendered`)

If the inventory has the expected field names, the renderer produces one config per device.

We will start by creating our inline inputs using `argparse`:

```python
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
```

You can see that we have the following:

- `--template`: (Mandatory) This is the path to the Jinja template
- `--inventory`: (Mandatory) Ths is the path to the inventory file
- `--format`: (Optional. Defaults to `auto`) This is the format type. It can only be one of the following: _auto, csv, json or xml_
- `--output-dir`: (Optional. Defaults to `rendered`)

Now, if the selected option in `--format` is _auto_, use this function:

```python
def detect_inventory_format(inventory_path: str) -> str:
    """Infer inventory format from file extension."""
    if inventory_path.lower().endswith(".csv"):
        return "csv"

    if inventory_path.lower().endswith(".json"):
        return "json"

    if inventory_path.lower().endswith(".xml"):
        return "xml"
```

This checks the path provided in `--inventory` and determines if it ends in any of the supported formats. If so, it returns that format name.

Next, we load the template using the Jinja library using the same `load_template()` function that we used earlier.

Following that, we load our inventory values using the `load_inventory()` function. Depending on the format type, we use a different function, as seen here:

```python
def load_inventory(inventory_path: str, format_type: str) -> list[dict]:
    """Load inventory based on file format."""
    if format_type == "csv":
        return load_inventory_csv(inventory_path)

    if format_type == "json":
        return load_inventory_json(inventory_path)

    if format_type == "xml":
        return load_inventory_xml(inventory_path)
```

For the case of _csv_, we use the same `load_inventory_csv()` function as before. For _json_, we use `load_inventory_json()`:

```python
def load_inventory_json(inventory_path: str) -> list[dict]:
    """Load device inventory from a JSON file."""
    print("\n📂 Loading inventory from JSON file...\n")
    with open(inventory_path, encoding="utf-8") as f:
        inventory = json.load(f)
        print(inventory)
        return inventory
```

What this does is that it opens the inventory file, gets the contents and converts them into a Python dictionary using the JSON library.

> But wait, **what is a Python dictionary?**: A dictionary is a simple `key: value` data structure, like a label and its value (example: `"BRANCH_HOSTNAME": "RTR-BOS-01"`).

Now, for the _xml_ case, the function `load_inventory_xml()` is a bit more cumbersome:

```python
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
```

What this function does, step by step:

```text
inventory.xml
    |
    v
ET.parse(...)  -->  root
    |
    v
root = <inventory>
    |
    +--> child: <device>  (device #1)
    |       |
    |       +--> children of <device>:
    |       |      <BRANCH_HOSTNAME>RTR-BOS-01</BRANCH_HOSTNAME>
    |       |      <BRANCH_IP>10.0.1.1</BRANCH_IP>
    |       |      <BRANCH_SUBNET>255.255.255.0</BRANCH_SUBNET>
    |       |      <WAN_IP>203.0.113.1</WAN_IP>
    |       |
    |       +--> build dictionary for this device:
    |              {
    |                "BRANCH_HOSTNAME": "RTR-BOS-01",
    |                "BRANCH_IP": "10.0.1.1",
    |                "BRANCH_SUBNET": "255.255.255.0",
    |                "WAN_IP": "203.0.113.1"
    |              }
    |
    +--> child: <device>  (device #2)
    +--> child: <device>  (device #3)
    +--> child: <device>  (device #4)
    +--> child: <device>  (device #5)
            (same process repeats)

final inventory list:
[
  {device #1 dictionary},
  {device #2 dictionary},
  {device #3 dictionary},
  {device #4 dictionary},
  {device #5 dictionary}
]
```

In this context, a **child** is any element directly inside another element. The diagram shows two child relationships: `<device>` is a child of `<inventory>`, and fields like `<BRANCH_IP>` are children of `<device>`.

In plain words: the function converts XML device blocks into the same Python list-of-dictionaries structure used by CSV/JSON, so rendering works the same way.

---

## 🏃‍♂️ Running the Renderer

Activate the shared virtual environment from the `session-01-foundations/` folder (create it if you haven't yet: see Session 02 for instructions):

```bash
cd session-01-foundations
source .venv/bin/activate
```

Then navigate into the lesson subfolder before running the script:

```bash
cd 04-structured-data
```

Run with JSON inventory (format is auto-detected):

```bash
python config_renderer.py --template ../02-howto-templates/branch-site-template-ios.j2 --inventory inventory.json --output-dir ./rendered
```

Run with XML inventory (same command pattern):

```bash
python config_renderer.py --template ../02-howto-templates/branch-site-template-ios.j2 --inventory inventory.xml --output-dir ./rendered
```

If needed, you can still force the format explicitly:

```bash
python config_renderer.py --template ../02-howto-templates/branch-site-template-ios.j2 --inventory inventory.xml --format xml --output-dir ./rendered
```

You will get the exact same results from both different data structures:

```bash
✅ Rendered config saved to ./rendered/RTR-BOS-01.cfg
✅ Rendered config saved to ./rendered/RTR-NYC-01.cfg
✅ Rendered config saved to ./rendered/RTR-SFO-01.cfg
✅ Rendered config saved to ./rendered/RTR-CHI-01.cfg
✅ Rendered config saved to ./rendered/RTR-DEN-01.cfg
```

---

## ⚖️ JSON vs XML - When to Use Which

| | JSON | XML |
|---|---|---|
| Typical source | NetBox/Nautobot exports, Ansible facts, Infrahub | SolarWinds reports, legacy IPAM exports, Cisco Prime |
| Python module | `json` (built-in) | `xml.etree.ElementTree` (built-in) |
| Readability | High | Moderate |
| Supports namespaces | No | Yes |
| Supports attributes | No | Yes |

---

## 🧠 Concept Mapping

| Data concept | Network engineering equivalent |
|---|---|
| JSON object `{}` | A single device record in a provisioning system |
| JSON array `[]` | A device inventory table |
| XML element | A config stanza (`interface`, `ip address`) |
| XML attribute | An inline qualifier (`name="GigabitEthernet0/0"`) |
| `json.load()` | Importing a CSV into Excel |
| `ET.parse()` | Opening a NETCONF RPC reply in a text editor |

---

## 🚀 What's Next

Now that you can read and normalize CSV, JSON, and XML inputs, you are ready to move from data preparation into live network interaction. In **Session 02**, you will connect to real sandbox devices, collect operational state, validate expected behavior, and apply small, controlled remediations using both pyATS and Ansible workflows.

That is the bridge to **Session 02: Interaction and Validation Workflows**.