import shutil
import os
import uuid
from typing import Callable, List
from .base import BaseRunner

class AmassRunner(BaseRunner):
    def __init__(self):
        local_bin = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "bin", "amass")
        binary = local_bin if os.path.exists(local_bin) else (shutil.which("amass") or "amass")
        super().__init__("amass", binary)
        
    def run_recon(self, target: str, on_line: Callable[[str], None], on_error: Callable[[str], None], timeout: int = 3600) -> List[str]:
        output_file = f"/tmp/amass_{uuid.uuid4().hex}.txt"
        
        # Using amass enum -passive by default for speed, and limiting to 5 minutes to prevent hanging
        args = ["enum", "-passive", "-d", target, "-timeout", "5", "-o", output_file]
        
        # We can stream stdout/stderr for logs
        self.run(args, on_line, on_error, timeout)
        
        results = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                results = [line.strip() for line in f if line.strip()]
            os.remove(output_file)
            
        return results
