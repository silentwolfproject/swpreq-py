import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional

from .client import Client
from .response import Response
from .streaming import ResponseStream
from .sse import SseStream
from .retry import RetryPolicy
from .connector import TCPConnector
from .trace import TraceConfig
from .auth import DigestAuth


class AsyncClient:
    def __init__(self, max_workers: int = 32, **client_kwargs):
        self._sync = Client(**client_kwargs)
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers, thread_name_prefix="swpreq"
        )

    async def _run(self, fn, *args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            self._executor, lambda: fn(*args, **kwargs)
        )


    def set_header(self, key: str, value: str) -> "AsyncClient":
        self._sync.set_header(key, value)
        return self

    def update_headers(self, headers: dict) -> "AsyncClient":
        self._sync.update_headers(headers)
        return self

    def remove_header(self, key: str) -> "AsyncClient":
        self._sync.remove_header(key)
        return self

    def clear_headers(self) -> "AsyncClient":
        self._sync.clear_headers()
        return self

    def set_cookie(self, name: str, value: str, domain: str) -> "AsyncClient":
        self._sync.set_cookie(name, value, domain)
        return self

    def clear_cookies(self) -> "AsyncClient":
        self._sync.clear_cookies()
        return self

    def set_retry(self, policy: RetryPolicy) -> "AsyncClient":
        self._sync.set_retry(policy)
        return self

    def mount(self, prefix: str, client) -> "AsyncClient":
        self._sync.mount(prefix, client)
        return self

    def unmount(self, prefix: str) -> "AsyncClient":
        self._sync.unmount(prefix)
        return self

    def register_request_hook(self, fn) -> "AsyncClient":
        self._sync.register_request_hook(fn)
        return self

    def register_response_hook(self, fn) -> "AsyncClient":
        self._sync.register_response_hook(fn)
        return self

    def multipart(self):
        return self._sync.multipart()

    def stream(self, method: str, url: str, **kw) -> ResponseStream:
        return self._sync.stream(method, url, **kw)

    def sse(self, url: str, headers=None, timeout=None) -> SseStream:
        return self._sync.sse(url, headers=headers, timeout=timeout)


    async def get(self, url: str, **kw) -> Response:
        return await self._run(self._sync.get, url, **kw)

    async def post(self, url: str, **kw) -> Response:
        return await self._run(self._sync.post, url, **kw)

    async def put(self, url: str, **kw) -> Response:
        return await self._run(self._sync.put, url, **kw)

    async def delete(self, url: str, **kw) -> Response:
        return await self._run(self._sync.delete, url, **kw)

    async def patch(self, url: str, **kw) -> Response:
        return await self._run(self._sync.patch, url, **kw)

    async def head(self, url: str, **kw) -> Response:
        return await self._run(self._sync.head, url, **kw)

    async def options(self, url: str, **kw) -> Response:
        return await self._run(self._sync.options, url, **kw)

    async def request(self, method: str, url: str, **kw) -> Response:
        return await self._run(self._sync.request, method, url, **kw)


    async def gather(self, *coros):
        return await asyncio.gather(*coros)

    async def map(self, urls, method: str = "GET", **kw):
        tasks = [self.request(method, u, **kw) for u in urls]
        return await asyncio.gather(*tasks)

    async def close(self):
        self._executor.shutdown(wait=True)
        self._sync.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()


AsyncSession = AsyncClient