from typing import List, Dict, Set
from .models.domain import ReconResult

def merge_results(subfinder_domains: List[str], amass_domains: List[str]) -> Dict[str, ReconResult]:
    merged: Dict[str, ReconResult] = {}
    
    for domain in subfinder_domains:
        d = domain.lower().strip()
        if not d: continue
        if d not in merged:
            merged[d] = ReconResult(domain=d, sources=set())
        merged[d].sources.add("subfinder")
        
    for domain in amass_domains:
        d = domain.lower().strip()
        if not d: continue
        if d not in merged:
            merged[d] = ReconResult(domain=d, sources=set())
        merged[d].sources.add("amass")
        
    return merged

def update_with_httpx(merged: Dict[str, ReconResult], httpx_results: List[Dict]) -> None:
    for res in httpx_results:
        # httpx output usually contains "input" which is the original domain requested
        domain = res.get("input", "").lower().strip()
        if not domain:
            continue
            
        if domain in merged:
            merged[domain].is_alive = True
            merged[domain].status_code = res.get("status_code")
            merged[domain].title = res.get("title")
            
            # Extract IP
            host_info = res.get("host")
            if host_info and isinstance(host_info, str):
                merged[domain].ip = host_info
            
            merged[domain].webserver = res.get("webserver")
