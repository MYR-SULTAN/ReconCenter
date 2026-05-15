import subprocess
import shutil
import os
from typing import Dict

def check_tools() -> Dict[str, bool]:
    """Check if required tools are available in the system PATH or local bin."""
    tools = {
        "subfinder": False,
        "amass": False,
        "httpx": False
    }
    
    local_bin_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bin")
    
    for tool in tools.keys():
        local_path = os.path.join(local_bin_dir, tool)
        if os.path.exists(local_path) or shutil.which(tool) is not None or (tool == "httpx" and shutil.which("httpx-toolkit")):
            tools[tool] = True
            
    return tools

def get_tool_version(tool_name: str) -> str:
    """Get the version of the tool if installed."""
    if shutil.which(tool_name) is None:
        return "Not installed"
    
    try:
        # Most of these tools support -version
        result = subprocess.run([tool_name, "-version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.split('\n')[0].strip()
        return "Unknown version"
    except Exception as e:
        return f"Error: {str(e)}"
