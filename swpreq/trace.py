from dataclasses import dataclass
from typing import Any, Callable, List, Optional


@dataclass
class TraceContext:
    event: str
    url: str
    method: str
    status: Optional[int] = None
    error: Optional[str] = None
    elapsed_ms: int = 0


class TraceConfig:
    def __init__(self):
        self.on_request_start: List[Callable] = []
        self.on_request_end: List[Callable] = []
        self.on_request_redirect: List[Callable] = []
        self.on_request_retry: List[Callable] = []
        self.on_response_start: List[Callable] = []
        self.on_response_end: List[Callable] = []
        self.on_response_chunk: List[Callable] = []
        self.on_connection_create: List[Callable] = []
        self.on_connection_reuse: List[Callable] = []
        self.on_dns_resolve: List[Callable] = []
        self.on_dns_cache_hit: List[Callable] = []
        self.on_tls_handshake_start: List[Callable] = []
        self.on_tls_handshake_end: List[Callable] = []

    def emit(self, ctx: TraceContext):
        callbacks = {
            "request_start": self.on_request_start,
            "request_end": self.on_request_end,
            "request_redirect": self.on_request_redirect,
            "request_retry": self.on_request_retry,
            "response_start": self.on_response_start,
            "response_end": self.on_response_end,
            "response_chunk": self.on_response_chunk,
            "connection_create": self.on_connection_create,
            "connection_reuse": self.on_connection_reuse,
            "dns_resolve": self.on_dns_resolve,
            "dns_cache_hit": self.on_dns_cache_hit,
            "tls_handshake_start": self.on_tls_handshake_start,
            "tls_handshake_end": self.on_tls_handshake_end,
        }.get(ctx.event, [])

        for cb in callbacks:
            try:
                cb(ctx)
            except Exception:
                pass