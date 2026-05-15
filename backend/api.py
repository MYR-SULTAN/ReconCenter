import threading
import time
import json
import logging
import re
from typing import Dict, Any, List

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')

from .models.domain import ScanConfig
from .runners import SubfinderRunner, AmassRunner, HttpxRunner
from .parsers import merge_results, update_with_httpx
from .storage.db import save_scan, update_scan_status, save_scan_results, get_history, get_scan_results
from .utils.health import check_tools

logger = logging.getLogger(__name__)

class Api:
    def __init__(self):
        self.window = None
        self.active_runners = []
        self._stop_event = threading.Event()
        self.is_scanning = False

    def set_window(self, window):
        self.window = window
        
    def _emit(self, event_name: str, payload: Any):
        if self.window:
            try:
                # Using evaluate_js to call a global handler in JS
                # Ensure payload is JSON serializable
                json_payload = json.dumps(payload)
                self.window.evaluate_js(f"window.dispatchEvent(new CustomEvent('{event_name}', {{detail: {json_payload}}}))")
            except Exception as e:
                logger.error(f"Failed to emit event {event_name}: {e}")

    def _log(self, message: str, level: str = "info"):
        clean_msg = ansi_escape.sub('', message)
        self._emit("log", {"message": clean_msg, "level": level})
        if level == "error":
            logger.error(message)
        else:
            logger.info(message)

    def check_health(self) -> Dict[str, bool]:
        """Called by frontend on load to check tools status"""
        return check_tools()

    def get_history(self) -> List[Dict[str, Any]]:
        return get_history()
        
    def get_scan(self, scan_id: int) -> List[Dict[str, Any]]:
        return get_scan_results(scan_id)

    def stop_scan(self):
        if self.is_scanning:
            self._log("Stopping scan requested...", "warning")
            self._stop_event.set()
            for runner in self.active_runners:
                runner.stop()
            return True
        return False

    def start_scan(self, config_dict: Dict[str, Any]) -> bool:
        if self.is_scanning:
            return False
            
        self.is_scanning = True
        self._stop_event.clear()
        self.active_runners = []
        
        # Start scanning in a separate thread so we don't block pywebview
        thread = threading.Thread(target=self._run_scan_thread, args=(config_dict,))
        thread.daemon = True
        thread.start()
        return True

    def _run_scan_thread(self, config_dict: Dict[str, Any]):
        start_time = time.time()
        raw_target = config_dict.get("target", "").strip()
        
        # Clean the target (remove http://, https://, and paths)
        clean_target = re.sub(r'^https?://', '', raw_target)
        target = clean_target.split('/')[0]
        
        tools = config_dict.get("tools", {})
        
        use_subfinder = tools.get("subfinder", False)
        use_amass = tools.get("amass", False)
        use_httpx = tools.get("httpx", False)
        
        used_tools = []
        if use_subfinder: used_tools.append("subfinder")
        if use_amass: used_tools.append("amass")
        if use_httpx: used_tools.append("httpx")

        scan_id = save_scan(target, used_tools, "running")
        self._emit("scan_started", {"scan_id": scan_id, "target": target})
        self._log(f"Starting scan on {target}")

        subfinder_results = []
        amass_results = []

        try:
            # Subfinder
            if use_subfinder and not self._stop_event.is_set():
                self._emit("progress", {"stage": "subfinder", "message": "Running Subfinder..."})
                runner = SubfinderRunner()
                self.active_runners.append(runner)
                
                def on_subfinder_error(err):
                    self._log(f"[subfinder] {err}", "error")
                    
                subfinder_results = runner.run_recon(target, lambda x: None, on_subfinder_error)
                self._log(f"Subfinder found {len(subfinder_results)} domains", "success")

            # Amass
            if use_amass and not self._stop_event.is_set():
                self._emit("progress", {"stage": "amass", "message": "Running Amass..."})
                runner = AmassRunner()
                self.active_runners.append(runner)
                
                def on_amass_line(line):
                    # We can log amass output if we want, but it might be verbose
                    pass
                def on_amass_error(err):
                    err_lower = err.lower()
                    if "libpostal" in err_lower or "address_parser" in err_lower or "address parser" in err_lower or "parser model" in err_lower:
                        return
                    self._log(f"[amass] {err}", "error")
                    
                amass_results = runner.run_recon(target, on_amass_line, on_amass_error)
                self._log(f"Amass found {len(amass_results)} domains", "success")

            # Merge
            if self._stop_event.is_set():
                raise Exception("Scan stopped by user")
                
            self._emit("progress", {"stage": "merging", "message": "Merging and deduplicating..."})
            merged_dict = merge_results(subfinder_results, amass_results)
            all_domains = list(merged_dict.keys())
            self._log(f"Total unique domains after deduplication: {len(all_domains)}", "info")

            # Httpx
            if use_httpx and all_domains and not self._stop_event.is_set():
                self._emit("progress", {"stage": "httpx", "message": "Running Httpx for alive checking..."})
                runner = HttpxRunner()
                self.active_runners.append(runner)
                
                def on_httpx_error(err):
                    self._log(f"[httpx] {err}", "error")
                    
                httpx_data = runner.run_recon(all_domains, lambda x: None, on_httpx_error)
                self._log(f"Httpx found {len(httpx_data)} alive subdomains", "success")
                update_with_httpx(merged_dict, httpx_data)

            # Finalize
            if self._stop_event.is_set():
                raise Exception("Scan stopped by user")

            final_results = [r.to_dict() for r in merged_dict.values()]
            alive_count = sum(1 for r in final_results if r.get("is_alive"))

            save_scan_results(scan_id, final_results)
            update_scan_status(scan_id, "completed", len(final_results), alive_count)

            elapsed = time.time() - start_time
            self._log(f"Scan completed in {elapsed:.2f}s", "success")
            
            self._emit("scan_finished", {
                "scan_id": scan_id,
                "status": "completed",
                "results": final_results,
                "total": len(final_results),
                "alive": alive_count,
                "elapsed": elapsed
            })

        except Exception as e:
            logger.error(f"Scan error: {str(e)}")
            self._log(f"Scan failed: {str(e)}", "error")
            status = "stopped" if self._stop_event.is_set() else "error"
            update_scan_status(scan_id, status)
            self._emit("scan_finished", {"scan_id": scan_id, "status": status, "results": []})
        finally:
            self.is_scanning = False
            self.active_runners = []
            self._stop_event.clear()
