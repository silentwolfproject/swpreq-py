import ctypes
import json as _json_module
from typing import Any, Dict, Optional

from . import _native
from .exceptions import SwpreqError, raise_for_code
from .response import Response
from .retry import RetryPolicy
from .hooks import Hooks
from .streaming import ResponseStream
from .sse import SseStream
from .multipart import MultipartBuilder


def _parse_response(ptr) -> Response:
    lib = _native.get_lib()
    try:
        r = ptr.contents

        if r.error:
            msg = r.error.decode("utf-8", errors="replace")
            code = 99
            if ":" in msg:
                head, tail = msg.split(":", 1)
                try:
                    code = int(head.strip())
                    msg = tail.strip()
                except ValueError:
                    pass
            raise_for_code(code, msg)

        if r.body_len > 0 and r.body:
            body = ctypes.string_at(r.body, r.body_len)
        else:
            body = b""

        headers = {}
        if r.headers_json:
            try:
                headers = _json_module.loads(r.headers_json.decode("utf-8"))
            except Exception:
                headers = {}

        return Response(
            status_code=r.status_code,
            body=body,
            headers=headers,
            url=r.url.decode("utf-8") if r.url else "",
            elapsed_ms=r.elapsed_ms,
            http_version=r.http_version,
        )
    finally:
        lib.swpreq_response_free(ptr)


class Client:
    def __init__(
        self,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        pool_size: int = 100,
        http2: bool = True,
        redirect_limit: int = 10,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
        verify: bool = True,
        retry: Optional[RetryPolicy] = None,
        hooks: Optional[Hooks] = None,
        trust_env: bool = True,
    ):
        self._config = {
            "timeout_ms": int(timeout * 1000),
            "connect_timeout_ms": int(connect_timeout * 1000),
            "pool_size": pool_size,
            "http2": http2,
            "redirect_limit": redirect_limit,
            "danger_accept_invalid_certs": not verify,
        }
        if proxy:
            self._config["proxy"] = proxy
        if user_agent:
            self._config["user_agent"] = user_agent

        lib = _native.get_lib()
        cfg_json = _json_module.dumps(self._config).encode("utf-8")
        self._handle = lib.swpreq_client_new(cfg_json)
        if not self._handle:
            raise SwpreqError("failed to create client")

        self._default_headers: Dict[str, str] = {}
        self._default_cookies: Dict[str, str] = {}
        self._retry: RetryPolicy = retry or RetryPolicy()
        self._hooks: Hooks = hooks or Hooks()
        self._adapters: Dict[str, "Client"] = {}
        self.trust_env = trust_env
        self.timeout = timeout
        self.verify = verify

        self._apply_retry()

    def _apply_retry(self) -> None:
        lib = _native.get_lib()
        if hasattr(lib, "swpreq_client_set_retry"):
            lib.swpreq_client_set_retry(
                self._handle,
                self._retry.max_retries,
                self._retry.base_delay_ms,
                1 if self._retry.exponential else 0,
                1 if self._retry.jitter else 0,
            )

    def set_retry(self, policy: RetryPolicy) -> "Client":
        self._retry = policy
        self._apply_retry()
        return self

    def mount(self, prefix: str, client: "Client") -> "Client":
        self._adapters[prefix] = client
        return self

    def unmount(self, prefix: str) -> "Client":
        self._adapters.pop(prefix, None)
        return self

    def _resolve_client(self, url: str) -> "Client":
        best_prefix = ""
        best_client = self
        for prefix, client in self._adapters.items():
            if url.startswith(prefix) and len(prefix) > len(best_prefix):
                best_prefix = prefix
                best_client = client
        return best_client

    def register_request_hook(self, fn) -> "Client":
        self._hooks.register_request(fn)
        return self

    def register_response_hook(self, fn) -> "Client":
        self._hooks.register_response(fn)
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self):
        if getattr(self, "_handle", None):
            _native.get_lib().swpreq_client_free(self._handle)
            self._handle = None

    def set_header(self, key: str, value: str) -> "Client":
        lib = _native.get_lib()
        code = lib.swpreq_set_default_header(
            self._handle,
            key.encode("utf-8"),
            value.encode("utf-8"),
        )
        if code != 0:
            raise SwpreqError(f"failed to set header: {code}")
        self._default_headers[key] = value
        return self

    def remove_header(self, key: str) -> "Client":
        lib = _native.get_lib()
        if hasattr(lib, "swpreq_remove_default_header"):
            lib.swpreq_remove_default_header(self._handle, key.encode("utf-8"))
        self._default_headers.pop(key, None)
        return self

    def clear_headers(self) -> "Client":
        lib = _native.get_lib()
        if hasattr(lib, "swpreq_clear_default_headers"):
            lib.swpreq_clear_default_headers(self._handle)
        self._default_headers.clear()
        return self

    def update_headers(self, headers: Dict[str, str]) -> "Client":
        for k, v in headers.items():
            self.set_header(k, v)
        return self

    def set_cookie(self, name: str, value: str, domain: str) -> "Client":
        lib = _native.get_lib()
        if hasattr(lib, "swpreq_set_cookie"):
            lib.swpreq_set_cookie(
                self._handle,
                name.encode("utf-8"),
                value.encode("utf-8"),
                domain.encode("utf-8"),
            )
        self._default_cookies[name] = value
        return self

    def clear_cookies(self) -> "Client":
        lib = _native.get_lib()
        if hasattr(lib, "swpreq_clear_cookies"):
            lib.swpreq_clear_cookies(self._handle)
        self._default_cookies.clear()
        return self

    def _request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[bytes] = None,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        timeout: Optional[float] = None,
        proxy: Optional[str] = None,
        allow_redirects: Optional[bool] = None,
        max_redirects: Optional[int] = None,
        files: Optional[MultipartBuilder] = None,
        stream: bool = False,
        encoding: Optional[str] = None,
    ) -> Response:
        resolved = self._resolve_client(url)
        if resolved is not self:
            return resolved._request(
                method, url, headers=headers, params=params, body=body,
                data=data, json=json, timeout=timeout, proxy=proxy,
                allow_redirects=allow_redirects, max_redirects=max_redirects,
                files=files, stream=stream, encoding=encoding,
            )

        lib = _native.get_lib()

        if params:
            from urllib.parse import urlencode, urlparse, urlunparse, parse_qsl

            parsed = urlparse(url)
            existing = parse_qsl(parsed.query)
            merged_params = existing + [(str(k), str(v)) for k, v in params.items()]
            url = urlunparse(parsed._replace(query=urlencode(merged_params)))

        request_headers: Dict[str, str] = {}
        if headers:
            request_headers.update(headers)

        body_bytes = body
        content_type_override = None

        if files is not None:
            content_type_override, body_bytes = files.build()
        elif json is not None:
            body_bytes = _json_module.dumps(json, separators=(",", ":")).encode("utf-8")
            content_type_override = "application/json"
        elif data is not None:
            if isinstance(data, dict):
                from urllib.parse import urlencode

                body_bytes = urlencode(data).encode("utf-8")
                content_type_override = "application/x-www-form-urlencoded"
            elif isinstance(data, str):
                body_bytes = data.encode("utf-8")
            elif isinstance(data, bytes):
                body_bytes = data

        if content_type_override:
            if not any(k.lower() == "content-type" for k in request_headers):
                request_headers["Content-Type"] = content_type_override

        if self._default_cookies:
            cookie_str = "; ".join(
                f"{k}={v}" for k, v in self._default_cookies.items()
            )
            if not any(k.lower() == "cookie" for k in request_headers):
                request_headers["Cookie"] = cookie_str

        request_context = {
            "method": method,
            "url": url,
            "headers": request_headers,
            "body": body_bytes,
            "timeout": timeout,
            "proxy": proxy,
        }
        request_context = self._hooks.apply_request(request_context)

        headers_json = _json_module.dumps(
            request_context["headers"]
        ).encode("utf-8")
        timeout_ms = int(request_context["timeout"] * 1000) if request_context["timeout"] else 0
        proxy_val = request_context.get("proxy")
        proxy_bytes = proxy_val.encode("utf-8") if proxy_val else None

        body_arr = None
        body_ptr = None
        body_len = 0
        if request_context["body"]:
            body_len = len(request_context["body"])
            if body_len > 0:
                body_arr = (ctypes.c_uint8 * body_len).from_buffer_copy(
                    request_context["body"]
                )
                body_ptr = ctypes.cast(body_arr, ctypes.POINTER(ctypes.c_uint8))

        if allow_redirects is None:
            follow_flag = -1
        elif allow_redirects:
            follow_flag = 1
        else:
            follow_flag = 0

        redirect_limit_val = -1
        if max_redirects is not None:
            redirect_limit_val = max_redirects

        resp_ptr = lib.swpreq_request_sync(
            self._handle,
            method.encode("utf-8"),
            url.encode("utf-8"),
            headers_json,
            body_ptr,
            body_len,
            timeout_ms,
            proxy_bytes,
            redirect_limit_val,
            follow_flag,
        )
        if not resp_ptr:
            raise SwpreqError("null response from native layer")

        response = _parse_response(resp_ptr)
        response = self._hooks.apply_response(response)

        if stream:
            response.stream = ResponseStream(
                self, url, headers=headers, timeout=timeout
            )

        if encoding:
            response._force_encoding = encoding

        return response

    def get(self, url: str, **kw) -> Response:
        return self._request("GET", url, **kw)

    def post(self, url: str, **kw) -> Response:
        return self._request("POST", url, **kw)

    def put(self, url: str, **kw) -> Response:
        return self._request("PUT", url, **kw)

    def delete(self, url: str, **kw) -> Response:
        return self._request("DELETE", url, **kw)

    def patch(self, url: str, **kw) -> Response:
        return self._request("PATCH", url, **kw)

    def head(self, url: str, **kw) -> Response:
        return self._request("HEAD", url, **kw)

    def options(self, url: str, **kw) -> Response:
        return self._request("OPTIONS", url, **kw)

    def request(self, method: str, url: str, **kw) -> Response:
        return self._request(method, url, **kw)

    def get_json(self, url: str, **kw) -> Any:
        return self.get(url, **kw).json()

    def post_json(self, url: str, data: Any, **kw) -> Any:
        return self.post(url, json=data, **kw).json()

    def stream(self, method: str, url: str, **kw) -> ResponseStream:
        return ResponseStream(self, url, **kw)

    def sse(self, url: str, headers: Optional[dict] = None,
            timeout: Optional[float] = None) -> SseStream:
        return SseStream(self, url, headers=headers, timeout=timeout)

    def multipart(self) -> MultipartBuilder:
        return MultipartBuilder()

    def netrc_lookup(self, host: str):
        lib = _native.get_lib()
        if not hasattr(lib, "swpreq_netrc_lookup"):
            return None
        login_out = ctypes.c_char_p()
        password_out = ctypes.c_char_p()
        code = lib.swpreq_netrc_lookup(
            self._handle,
            host.encode("utf-8"),
            ctypes.byref(login_out),
            ctypes.byref(password_out),
        )
        if code != 0:
            return None
        result = (login_out.value.decode("utf-8"),
                  password_out.value.decode("utf-8"))
        lib.swpreq_string_free(login_out)
        lib.swpreq_string_free(password_out)
        return result


Session = Client