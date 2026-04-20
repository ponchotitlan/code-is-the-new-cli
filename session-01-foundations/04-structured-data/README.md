# 📦 Session 04: Structured Data for Network Engineers - JSON and XML Parsing
Topics: 📄 JSON · 🌐 XML · 🔍 Parsing · 🔧 Adapting tools

---

## 🎯 By the end of this session you will be able to:

| # | Skill |
|:---:|:---|
| 1 | 📄 Read and understand JSON payloads returned by network REST APIs |
| 2 | 🌐 Navigate XML documents returned by NETCONF and legacy device APIs |
| 3 | 🔍 Extract specific values from nested JSON and XML structures with Python |
| 4 | 🔄 Adapt `config_renderer.py` to accept JSON or XML as inventory input |
| 5 | ⚖️ Choose the right format for the job based on the data source |

---

## 🗺️ What is going on

<div align="center"><img src="../../images/citnc_banner_04.png" width="80%"/></div></br>

---

Alice points the renderer at the team's new provisioning API - and it breaks immediately. The API speaks JSON, not CSV. Bob pulls a NETCONF backup from a legacy router and gets an XML document nobody is sure how to read. Poncho finds a vendor Python SDK that returns a mix of both formats depending on the endpoint.

They have a working tool. Now they need to understand the data it will process in the real world. Before writing another line of code, they learn to *read* the formats that network APIs actually use.

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

Parsing it in Python:

```python
import json

with open("inventory.json", encoding="utf-8") as f:
    devices = json.load(f)

for device in devices:
    print(device["BRANCH_HOSTNAME"])
```

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

Parsing it in Python using the built-in `xml.etree.ElementTree`:

```python
import xml.etree.ElementTree as ET

tree = ET.parse("inventory.xml")
root = tree.getroot()

for device in root.findall("device"):
    print(device.findtext("BRANCH_HOSTNAME"))
```

---

## 🔄 Adapting the Renderer

The renderer from Session 03 expects a CSV file. Adapting it to handle JSON or XML means replacing only the `load_inventory()` step - the template rendering logic stays exactly the same.

```python
def load_inventory_json(inventory_path: str) -> list[dict]:
    """Load device inventory from a JSON file."""
    with open(inventory_path, encoding="utf-8") as f:
        return json.load(f)


def load_inventory_xml(inventory_path: str) -> list[dict]:
    """Load device inventory from an XML file."""
    tree = ET.parse(inventory_path)
    return [
        {child.tag: child.text for child in device}
        for device in tree.getroot().findall("device")
    ]
```

A `--format` CLI argument selects which loader to use at runtime:

```bash
python config_renderer.py --template branch-site-template-ios.j2 \
                           --inventory inventory.json \
                           --format json \
                           --output-dir ./rendered
```

---

## ⚖️ JSON vs XML - When to Use Which

| | JSON | XML |
|---|---|---|
| Typical source | REST APIs, Ansible facts, Nautobot | NETCONF, legacy vendor CLIs, NX-API XML mode |
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
