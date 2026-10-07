import json as _json_module
from typing import Any, Dict, Optional


class Response:
    def __init__(
        self,
        status_code: int,
        body: bytes,
        headers: dict,
        url: str,
        elapsed_ms: int,
        http_version: int,
    ):
        self.status_code = status_code
        self._body = body
        self.headers: Dict[str, str] = dict(headers or {})
        self.url = url
        self.elapsed_ms = elapsed_ms
        self.http_version_num = http_version
        self.history = []
        self.cookies: Dict[str, str] = {}
        self.links: Dict[str, str] = {}
        self.stream = None
        self.request_id: Optional[str] = None
        self._force_encoding: Optional[str] = None
        self._parse_links()

    def _parse_links(self):
        link_header = self.header("Link") or self.header("link")
        if not link_header:
            return
        for part in link_header.split(","):
            if "<" in part and ">" in part and "rel=" in part:
                start = part.find("<") + 1
                end = part.find(">")
                url = part[start:end]
                rel_start = part.find('rel="') + 5
                rel_end = part.find('"', rel_start)
                rel = part[rel_start:rel_end]
                self.links[rel] = url

    @property
    def http_version(self) -> str:
        return {
            9: "0.9",
            10: "1.0",
            11: "1.1",
            20: "2",
            30: "3",
        }.get(self.http_version_num, "unknown")

    @property
    def content(self) -> bytes:
        return self._body

    @property
    def text(self) -> str:
        if self._force_encoding:
            return self._body.decode(self._force_encoding, errors="replace")
        return self._body.decode("utf-8", errors="replace")

    @property
    def encoding(self) -> str:
        if self._force_encoding:
            return self._force_encoding
        ct = self.header("Content-Type") or ""
        if "charset=" in ct:
            return ct.split("charset=")[-1].split(";")[0].strip()
        return "utf-8"

    def json(self) -> Any:
        return _json_module.loads(self.text)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            from .exceptions import HTTPError

            raise HTTPError(
                f"HTTP {self.status_code}",
                status_code=self.status_code,
                response=self,
            )

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    @property
    def is_success(self) -> bool:
        return 200 <= self.status_code < 300

    @property
    def is_redirect(self) -> bool:
        return 300 <= self.status_code < 400

    @property
    def is_client_error(self) -> bool:
        return 400 <= self.status_code < 500

    @property
    def is_server_error(self) -> bool:
        return self.status_code >= 500

    def header(self, name: str) -> Optional[str]:
        for k, v in self.headers.items():
            if k.lower() == name.lower():
                return v
        return None

    def cookie(self, name: str) -> Optional[str]:
        return self.cookies.get(name)

    def link(self, rel: str) -> Optional[str]:
        return self.links.get(rel)

    def has_next_page(self) -> bool:
        return "next" in self.links

    def next_page_url(self) -> Optional[str]:
        return self.links.get("next")

    def iter_content(self, chunk_size: int = 8192):
        for i in range(0, len(self._body), chunk_size):
            yield self._body[i:i + chunk_size]

    def __repr__(self) -> str:
        return f"<Response [{self.status_code}] {self.url}>"