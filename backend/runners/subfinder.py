import shutil
import os
import uuid
from typing import Callable, List
from .base import BaseRunner

class SubfinderRunner(BaseRunner):
    def __init__(self):
        current_dir = os.path.abspath(os.path.dirname(__file__))
        local_bin = os.path.join(os.path.dirname(os.path.dirname(current_dir)), "bin", "subfinder")
        binary = local_bin if os.path.exists(local_bin) else (shutil.which("subfinder") or "subfinder")
        super().__init__("subfinder", binary)
        
    def run_recon(self, target: str, on_line: Callable[[str], None], on_error: Callable[[str], None], timeout: int = 3600) -> List[str]:
        output_file = f"/tmp/subfinder_{uuid.uuid4().hex}.txt"
        args = ["-d", target, "-o", output_file, "-silent", "-duc"]
        
        # Stream stderr for progress/errors (subfinder might log to stderr even on silent for errors)
        self.run(args, lambda x: None, on_error, timeout)
        
        results = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                results = [line.strip() for line in f if line.strip()]
            os.remove(output_file)
            
        return results
