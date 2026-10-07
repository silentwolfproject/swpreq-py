import asyncio
import json
from typing import Any, Callable, Dict, List


class Request:
    def __init__(self, method, path, query, headers, body, params):
        self.method = method
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body
        self.params = params

    def json(self) -> Any:
        return json.loads(self.body.decode("utf-8"))

    def text(self) -> str:
        return self.body.decode("utf-8", errors="replace")


class Response:
    def __init__(self, body=None, status=200, content_type="application/json"):
        self.status = status
        self.content_type = content_type

        if isinstance(body, (dict, list)):
            self.body = json.dumps(body).encode("utf-8")
        elif isinstance(body, str):
            self.body = body.encode("utf-8")
        elif isinstance(body, bytes):
            self.body = body
        else:
            self.body = b""

    @classmethod
    def json(cls, data, status=200):
        return cls(body=data, status=status, content_type="application/json")

    @classmethod
    def text(cls, data, status=200):
        return cls(body=data, status=status, content_type="text/plain; charset=utf-8")

    @classmethod
    def html(cls, data, status=200):
        return cls(body=data, status=status, content_type="text/html; charset=utf-8")


class AsyncServer:
    def __init__(self, host="0.0.0.0", port=8080, **config):
        self.host = host
        self.port = port
        self.config = config
        self._routes: List = []
        self._middlewares: List = []
        self._ws_routes: List = []
        self._static: List = []

    def route(self, method: str, path: str):
        def decorator(fn):
            self._routes.append((method.upper(), path, fn))
            return fn
        return decorator

    def get(self, path: str):
        return self.route("GET", path)

    def post(self, path: str):
        return self.route("POST", path)

    def put(self, path: str):
        return self.route("PUT", path)

    def delete(self, path: str):
        return self.route("DELETE", path)

    def patch(self, path: str):
        return self.route("PATCH", path)

    def middleware(self, fn: Callable):
        self._middlewares.append(fn)
        return fn

    def ws(self, path: str):
        def decorator(fn):
            self._ws_routes.append((path, fn))
            return fn
        return decorator

    def mount_static(self, prefix: str, directory: str):
        self._static.append((prefix, directory))

    def run(self):
        from ._native import get_lib

        lib = get_lib()
        config = {"host": self.host, "port": self.port, **self.config}

        lib.swpreq_server_new(json.dumps(config).encode("utf-8"))
        lib.swpreq_server_run()

    async def run_async(self):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, self.run)