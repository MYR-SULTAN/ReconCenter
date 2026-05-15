import shutil
import os
import uuid
import json
from typing import Callable, List, Dict, Any
from .base import BaseRunner

class HttpxRunner(BaseRunner):
    def __init__(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        local_bin = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "bin", "httpx")
        binary = local_bin if os.path.exists(local_bin) else (shutil.which("httpx") or shutil.which("httpx-toolkit") or "httpx")
        super().__init__("httpx", binary)
        
    def run_recon(self, domains: List[str], on_line: Callable[[str], None], on_error: Callable[[str], None], timeout: int = 3600) -> List[Dict[str, Any]]:
        input_file = f"/tmp/httpx_in_{uuid.uuid4().hex}.txt"
        output_file = f"/tmp/httpx_out_{uuid.uuid4().hex}.json"
        
        with open(input_file, 'w') as f:
            for d in domains:
                f.write(d + "\n")
                
        args = ["-l", input_file, "-o", output_file, "-json", "-silent", "-title", "-status-code", "-ip", "-web-server"]
        
        # We can stream stderr for logs
        self.run(args, lambda x: None, on_error, timeout)
        
        results = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                for line in f:
                    if line.strip():
                        try:
                            results.append(json.loads(line))
                        except json.JSONDecodeError:
                            pass
            os.remove(output_file)
            
        if os.path.exists(input_file):
            os.remove(input_file)
            
        return results
