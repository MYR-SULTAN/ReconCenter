# Cyber Recon Command Center

A professional Desktop application using Python and `pywebview` to unify Subfinder, Amass, and httpx in a tactical, local-first dashboard.

## Overview
This application provides a seamless GUI for running command-line reconnaissance tools. It executes binaries locally via a Python backend and displays real-time results in a modern HTML/CSS/JS frontend without requiring any external web server.

## Architecture
- **Backend:** Python 3.11+, `pywebview` for the native window/bridge, `sqlite3` for history storage, `subprocess` for running tools.
- **Frontend:** Vanilla HTML, CSS, JS using ES Modules. No build process required for local dev.

---

## 🚀 Installation & Setup (Ubuntu)

### 1. Install System Dependencies
Make sure you have Go installed (required to install the recon tools), along with Python and pywebview dependencies:

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv golang gir1.2-webkit2-4.0
```

### 2. Install Recon Tools
You can install the tools using Go or download their binaries directly. Make sure they are in your system PATH.

```bash
# Subfinder
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Amass
go install -v github.com/owasp-amass/amass/v4/...@master

# httpx
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# Add Go binaries to your PATH (add this to ~/.bashrc or ~/.zshrc)
export PATH=$PATH:$(go env GOPATH)/bin
```

### 3. Setup Python Environment
```bash
cd rex
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 🛠️ Development

To run the application locally:
```bash
source venv/bin/activate
python app.py
```

---

## 📦 Packaging to Executable (PyInstaller)

Because we use `pywebview`, packaging the application into a single executable is straightforward with PyInstaller.

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable. We must include the `frontend` directory and our tools/resources:
```bash
pyinstaller --name "ReconCenter" \
            --windowed \
            --add-data "frontend:frontend" \
            app.py
```

3. The built executable will be available in the `dist/ReconCenter` folder.

> **Note:** The compiled application will still expect `subfinder`, `amass`, and `httpx` to be accessible on the target system's PATH.

---

## 🗺️ Roadmap & Future Expansion

This architecture is highly modular. You can easily extend it by adding new tools to `backend/runners/`.

1. **dnsx Integration:** Create `backend/runners/dnsx.py` to resolve domains and filter out dead DNS entries before passing to httpx.
2. **naabu Integration:** Create `backend/runners/naabu.py` for fast port scanning. Add a new checkbox in `index.html` and a parser to extract active ports.
3. **nuclei Integration:** Run templates on discovered alive hosts. This would require a new view in the frontend to display vulnerabilities.
4. **Screenshotting:** Use `gowitness` or `httpx -screenshot`. Update the UI to display an image gallery grid.
5. **Plugin System:** Implement a dynamic Python loader that checks a `plugins/` directory for `.py` files that inherit from `BaseRunner`. This allows the community to drop in new tools without modifying the core codebase.
