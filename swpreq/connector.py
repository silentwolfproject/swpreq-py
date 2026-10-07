from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TCPConnector:
    limit: int = 100
    limit_per_host: int = 0
    ttl_dns_cache: int = 10
    use_dns_cache: bool = True
    force_close: bool = False
    enable_cleanup_closed: bool = False
    keepalive_timeout: float = 15.0
    family: str = "any"
    ssl_verify: bool = True
    ssl_ca_file: Optional[str] = None
    ssl_cert_file: Optional[str] = None
    ssl_key_file: Optional[str] = None


@dataclass
class AsyncResolver:
    nameservers: List[str] = field(default_factory=lambda: ["8.8.8.8", "1.1.1.1"])
    ttl: int = 300


@dataclass
class UnixConnector:
    path: str = "/var/run/docker.sock"