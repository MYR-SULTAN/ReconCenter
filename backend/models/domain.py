from dataclasses import dataclass, field
from typing import List, Optional, Set
import datetime

@dataclass
class ToolConfig:
    tool_name: str
    enabled: bool
    args: List[str] = field(default_factory=list)

@dataclass
class ScanConfig:
    target: str
    tools: List[ToolConfig]
    output_dir: str
    is_file: bool = False
    timeout: int = 3600
    verbose: bool = False

@dataclass
class ReconResult:
    domain: str
    sources: Set[str] = field(default_factory=set)
    is_alive: Optional[bool] = None
    status_code: Optional[int] = None
    title: Optional[str] = None
    ip: Optional[str] = None
    webserver: Optional[str] = None
    
    def to_dict(self):
        return {
            "domain": self.domain,
            "sources": list(self.sources),
            "is_alive": self.is_alive,
            "status_code": self.status_code,
            "title": self.title,
            "ip": self.ip,
            "webserver": self.webserver
        }

@dataclass
class ScanHistory:
    id: int
    target: str
    timestamp: str
    tools_used: str
    total_domains: int
    alive_domains: int
    status: str
