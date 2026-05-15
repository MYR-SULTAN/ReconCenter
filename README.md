# Rex (Recon Engine X)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Powered by AI](https://img.shields.io/badge/Powered%20By-AI%20(80%25)-8A2BE2.svg)](#-credits--acknowledgments)

> **"Stop wrestling with terminals. Start hunting."**
> 
> *Rex is the ultimate local-first Command Center for Bug Bounty Hunters and Penetration Testers. It bridges the gap between raw hacking power and beautiful UI design.*

## 🎯 What is Rex?
Rex is an advanced **Information Gathering** and **Reconnaissance** GUI built for **Cyber Security** professionals, **Red Teamers**, and **Bug Bounty** hunters. If you do **Penetration Testing** or **OSINT**, this tool acts as your unified dashboard.

Instead of running individual commands, Rex seamlessly integrates world-class CLI tools (**Subfinder**, **Amass**, and **Httpx**) into a highly aesthetic, tactical HTML/CSS/JS frontend—without requiring any external web server. Perform blazing-fast **Subdomain Enumeration**, **Asset Discovery**, and **Live Host Checking** with a single click.

## Architecture
- **Backend:** Python 3.11+, `pywebview` for the native window/bridge, `sqlite3` for history storage, `subprocess` for running tools.
- **Frontend:** Vanilla HTML, CSS, JS using ES Modules. No build process required for local dev.

---

## 🚀 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/MYR-SULTAN/ReconCenter.git
cd ReconCenter
```

### 2. Install Recon Tools (Self-Contained Binaries)
For the best portable experience, download the pre-compiled binaries of the tools and place them in the `bin/` directory inside the project. The app will automatically detect them:

```bash
mkdir -p bin
cd bin
# Download and extract subfinder, amass, and httpx binaries here
# Ensure they are executable: chmod +x subfinder amass httpx
cd ..
```

### 3. Setup Python Virtual Environment (venv)
You must create a virtual environment so the application can run its GUI dependencies (like PyQt6) without breaking your system Python:

```bash
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install all required Python packages (including PyQt6 for the GUI)
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

---

## 🏆 Credits & Acknowledgments

- **MyrTech (ميرتك):** Project visionary and creator.
- **AI Assisted:** Approximately **80%** of this codebase was co-developed and accelerated by AI.
- Thanks to the open-source community for the amazing tools: [Subfinder](https://github.com/projectdiscovery/subfinder), [Amass](https://github.com/owasp-amass/amass), and [Httpx](https://github.com/projectdiscovery/httpx).

---
*Built with ❤️ by [MyrTech]*
