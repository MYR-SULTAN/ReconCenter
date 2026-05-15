import subprocess
import threading
import logging
from typing import Callable, List

logger = logging.getLogger(__name__)

class BaseRunner:
    def __init__(self, name: str, binary_path: str):
        self.name = name
        self.binary_path = binary_path
        self.process = None
        self.is_running = False
        
    def run(self, args: List[str], on_line: Callable[[str], None], on_error: Callable[[str], None], timeout: int = 3600):
        """Execute the command and stream output"""
        cmd = [self.binary_path] + args
        self.is_running = True
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            def read_stdout():
                for line in self.process.stdout:
                    if not self.is_running:
                        break
                    on_line(line.strip())
                    
            def read_stderr():
                for line in self.process.stderr:
                    if not self.is_running:
                        break
                    on_error(line.strip())
                    
            t1 = threading.Thread(target=read_stdout, daemon=True)
            t2 = threading.Thread(target=read_stderr, daemon=True)
            t1.start()
            t2.start()
            
            self.process.wait(timeout=timeout)
            t1.join()
            t2.join()
            
        except subprocess.TimeoutExpired:
            self.stop()
            on_error(f"[{self.name}] Execution timed out after {timeout} seconds.")
        except Exception as e:
            on_error(f"[{self.name}] Error: {str(e)}")
        finally:
            self.is_running = False

    def stop(self):
        self.is_running = False
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
