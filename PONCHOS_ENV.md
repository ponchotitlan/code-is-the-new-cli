# 🚀 Practical Dev Setup Guide (Super Simple)

This guide helps complete beginners set up the same kind of development environment used in this repo:

- Python
- Git + GitHub
- Visual Studio Code + useful extensions

It includes steps for Windows, macOS, and Linux.

---

## 🧰 1) The minimum tools you need

For this course/repo, install these first:

1. Python 3.11+ (3.12 or 3.13 are great choices)
2. Git
3. GitHub account
4. Visual Studio Code
5. VS Code extensions:
	 - Python (ms-python.python)
	 - Pylance (ms-python.vscode-pylance)
	 - Jupyter (ms-toolsai.jupyter)
	 - GitLens (eamodio.gitlens)
	 - GitHub Copilot Chat (github.copilot-chat, if you have the GitHub Copilot service)

---

## 🪟 2) Windows setup (easy path)

### 🧱 Step 1: Install Git

Option A (recommended): use winget in PowerShell:

```powershell
winget install --id Git.Git -e
```

Option B: download from https://git-scm.com/download/win

### 🐍 Step 2: Install Python

```powershell
winget install --id Python.Python.3.12 -e
```

Important during install: check the box "Add Python to PATH".

### 🧩 Step 3: Install VS Code

```powershell
winget install --id Microsoft.VisualStudioCode -e
```

### 🐙 Step 4: Create a GitHub account

Go to https://github.com and sign up.

### ✅ Step 5: Verify everything

Open PowerShell and run:

```powershell
python --version
pip --version
git --version
code --version
```

---

## 🍎 3) macOS setup (easy path)

### 🍺 Step 1: Install Homebrew (package manager)

In Terminal:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 🧱 Step 2: Install Git, Python, VS Code

```bash
brew install git python
brew install --cask visual-studio-code
```

### 🛠️ Step 3: Enable VS Code terminal command

In VS Code:

1. Open Command Palette (Cmd+Shift+P)
2. Search: Shell Command: Install 'code' command in PATH
3. Run it

### ✅ Step 4: Verify everything

```bash
python3 --version
pip3 --version
git --version
code --version
```

---

## 🐧 4) Linux setup (Ubuntu/Debian easy path)

### 📦 Step 1: Install Git + Python + pip + venv

```bash
sudo apt update
sudo apt install -y git python3 python3-pip python3-venv
```

### 🧩 Step 2: Install VS Code

```bash
sudo snap install code --classic
```

If you do not use snap, use the official Microsoft .deb package from:
https://code.visualstudio.com

### ✅ Step 3: Verify everything

```bash
python3 --version
pip3 --version
git --version
code --version
```

---

## 🔗 5) Connect Git with GitHub (all OS)

### 🪪 Step 1: Set your identity in Git

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### 🔐 Step 2: Generate SSH key

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

Press Enter for defaults.

### 🗝️ Step 3: Add SSH key to GitHub

Copy your public key:

- macOS/Linux:
	```bash
	cat ~/.ssh/id_ed25519.pub
	```
- Windows (PowerShell):
	```powershell
	type $env:USERPROFILE\.ssh\id_ed25519.pub
	```

Then:

1. Go to GitHub -> Settings -> SSH and GPG keys
2. Click New SSH key
3. Paste key and save

### ✅ Step 4: Test connection

```bash
ssh -T git@github.com
```

---

## 🧩 6) Install VS Code extensions (all OS)

In VS Code:

1. Open Extensions panel (left sidebar)
2. Search and install:
	 - Python (ms-python.python)
	 - Pylance (ms-python.vscode-pylance)
	 - Jupyter (ms-toolsai.jupyter)
	 - GitLens (eamodio.gitlens)
	 - GitHub Copilot Chat (github.copilot-chat, optional)

Or from terminal (if `code` command is available):

```bash
code --install-extension ms-python.python
code --install-extension ms-python.vscode-pylance
code --install-extension ms-toolsai.jupyter
code --install-extension eamodio.gitlens
code --install-extension github.copilot-chat
```

---

## 🧪 7) First project test (all OS)

Use this to confirm your setup works.

### 📁 Step 1: Create a folder and virtual environment

macOS/Linux:

```bash
mkdir hello-dev && cd hello-dev
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
mkdir hello-dev
cd hello-dev
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 📦 Step 2: Install a package

```bash
pip install requests
```

### ▶️ Step 3: Run a tiny Python script

Create file hello.py with:

```python
print("Environment is ready!")
```

Run:

```bash
python hello.py
```

If you see "Environment is ready!", your setup is working.

---

## 🛟 8) Troubleshooting

- "python not found": use python3 (macOS/Linux) or reinstall Python and ensure PATH is enabled.
- "code command not found": run "Shell Command: Install 'code' command in PATH" from VS Code.
- Git asks for credentials repeatedly: use SSH setup above instead of HTTPS.
- VS Code does not detect Python: press Cmd/Ctrl+Shift+P -> "Python: Select Interpreter" -> choose your .venv.

---

## 🧭 9) Recommended next step for this repo

From repo root, create and activate a virtual environment per session folder, then install each session's requirements.txt before running examples.

Example pattern:

```bash
cd session-03-models
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```