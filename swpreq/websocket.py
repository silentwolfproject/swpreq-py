import ctypes
import json as _json_module
import queue
from dataclasses import dataclass
from typing import Callable, Optional

from . import _native
from .exceptions import SwpreqError


@dataclass
class WebSocketMessage:
    type: str
    data: Optional[str] = None
    binary: Optional[bytes] = None
    code: Optional[int] = None
    reason: Optional[str] = None

    @property
    def is_text(self) -> bool:
        return self.type == "text"

    @property
    def is_binary(self) -> bool:
        return self.type == "binary"

    @property
    def is_close(self) -> bool:
        return self.type == "close"

    @property
    def is_ping(self) -> bool:
        return self.type == "ping"

    @property
    def is_pong(self) -> bool:
        return self.type == "pong"


_ON_MESSAGE_TYPE = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
)

_ON_EVENT_TYPE = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_char_p,
)


class AsyncWebSocket:
    def __init__(self, url: str, headers: Optional[dict] = None):
        self.url = url
        self.headers = headers or {}
        self._handle: Optional[int] = None
        self._on_message_cb: Optional[Callable] = None
        self._on_open_cb: Optional[Callable] = None
        self._on_close_cb: Optional[Callable] = None
        self._on_error_cb: Optional[Callable] = None
        self._callbacks_kept = []
        self._closed = False
        self._recv_queue: queue.Queue = queue.Queue()
        self._closed_event = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *args):
        await self.close()

    async def connect(self) -> None:
        import asyncio

        lib = _native.get_lib()

        headers_json = _json_module.dumps(self.headers or {}).encode("utf-8")
        handle_out = ctypes.c_int(0)
        error_out = ctypes.c_char_p()

        code = lib.swpreq_ws_connect(
            self.url.encode("utf-8"),
            headers_json,
            ctypes.byref(handle_out),
            ctypes.byref(error_out),
        )

        if code != 0:
            msg = error_out.value.decode("utf-8") if error_out.value else "unknown"
            if error_out.value:
                lib.swpreq_string_free(error_out)
            raise SwpreqError(f"WebSocket connect failed: {msg}")

        self._handle = handle_out.value
        self._closed_event = asyncio.Event()
        self._register_callbacks()

    def _register_callbacks(self):
        lib = _native.get_lib()
        instance = self

        def _on_message(user_data, msg_type, data_ptr, data_len):
            if data_ptr and data_len > 0:
                data = ctypes.string_at(data_ptr, data_len)
            else:
                data = b""

            if msg_type == 0:
                msg = WebSocketMessage(type="text", data=data.decode("utf-8", errors="replace"))
            elif msg_type == 1:
                msg = WebSocketMessage(type="binary", binary=data)
            else:
                msg = WebSocketMessage(type="unknown", data=data.decode("utf-8", errors="replace"))

            instance._recv_queue.put(msg)

            if instance._on_message_cb:
                try:
                    instance._on_message_cb(msg)
                except Exception:
                    pass

        def _on_open(user_data, code, reason):
            if instance._on_open_cb:
                try:
                    instance._on_open_cb()
                except Exception:
                    pass

        def _on_close(user_data, code, reason):
            reason_str = reason.decode("utf-8") if reason else ""
            close_msg = WebSocketMessage(type="close", code=code, reason=reason_str)
            instance._recv_queue.put(close_msg)

            if instance._on_close_cb:
                try:
                    instance._on_close_cb(code, reason_str)
                except Exception:
                    pass

            if instance._closed_event:
                try:
                    instance._closed_event.set()
                except Exception:
                    pass

        def _on_error(user_data, code, data_ptr, data_len):
            msg = ""
            if data_ptr and data_len > 0:
                msg = ctypes.string_at(data_ptr, data_len).decode("utf-8", errors="replace")
            err = SwpreqError(msg)
            instance._recv_queue.put(err)

            if instance._on_error_cb:
                try:
                    instance._on_error_cb(err)
                except Exception:
                    pass

        msg_cb = _ON_MESSAGE_TYPE(_on_message)
        open_cb = _ON_EVENT_TYPE(_on_open)
        close_cb = _ON_EVENT_TYPE(_on_close)
        err_cb = _ON_MESSAGE_TYPE(_on_error)

        self._callbacks_kept = [msg_cb, open_cb, close_cb, err_cb]

        code = lib.swpreq_ws_set_callbacks(
            self._handle,
            ctypes.cast(open_cb, ctypes.c_void_p),
            None,
            ctypes.cast(msg_cb, ctypes.c_void_p),
            None,
            ctypes.cast(err_cb, ctypes.c_void_p),
            None,
            ctypes.cast(close_cb, ctypes.c_void_p),
            None,
        )

        if code != 0:
            raise SwpreqError(f"WebSocket set_callbacks failed: {code}")

    def on_message(self, fn: Callable[[WebSocketMessage], None]) -> "AsyncWebSocket":
        self._on_message_cb = fn
        return self

    def on_open(self, fn: Callable[[], None]) -> "AsyncWebSocket":
        self._on_open_cb = fn
        return self

    def on_close(self, fn) -> "AsyncWebSocket":
        self._on_close_cb = fn
        return self

    def on_error(self, fn: Callable[[Exception], None]) -> "AsyncWebSocket":
        self._on_error_cb = fn
        return self

    async def send(self, data) -> None:
        if isinstance(data, str):
            await self.send_text(data)
        elif isinstance(data, bytes):
            await self.send_binary(data)
        else:
            raise SwpreqError(f"Unsupported data type: {type(data)}")

    async def send_text(self, text: str) -> None:
        if self._handle is None:
            raise SwpreqError("WebSocket not connected")
        lib = _native.get_lib()
        code = lib.swpreq_ws_send_text(self._handle, text.encode("utf-8"))
        if code != 0:
            raise SwpreqError(f"WebSocket send failed: {code}")

    async def send_binary(self, data: bytes) -> None:
        if self._handle is None:
            raise SwpreqError("WebSocket not connected")
        lib = _native.get_lib()
        if len(data) == 0:
            raise SwpreqError("Empty binary data")
        arr = (ctypes.c_uint8 * len(data)).from_buffer_copy(data)
        ptr = ctypes.cast(arr, ctypes.POINTER(ctypes.c_uint8))
        code = lib.swpreq_ws_send_binary(self._handle, ptr, len(data))
        if code != 0:
            raise SwpreqError(f"WebSocket send binary failed: {code}")

    async def send_json(self, obj) -> None:
        await self.send_text(_json_module.dumps(obj))

    async def send_ping(self) -> None:
        if self._handle is None:
            raise SwpreqError("WebSocket not connected")
        lib = _native.get_lib()
        code = lib.swpreq_ws_send_ping(self._handle)
        if code != 0:
            raise SwpreqError(f"WebSocket ping failed: {code}")

    async def recv(self, timeout: Optional[float] = None) -> WebSocketMessage:
        import asyncio

        if self._closed:
            raise SwpreqError("WebSocket closed")

        loop = asyncio.get_running_loop()

        def _blocking_recv():
            try:
                return self._recv_queue.get(timeout=timeout)
            except queue.Empty:
                return None

        msg = await loop.run_in_executor(None, _blocking_recv)

        if msg is None:
            raise SwpreqError("WebSocket recv timeout")

        if isinstance(msg, Exception):
            raise msg

        return msg

    async def close(self, code: int = 1000, reason: str = "") -> None:
        if self._handle is None:
            return
        lib = _native.get_lib()
        lib.swpreq_ws_close(self._handle)
        lib.swpreq_ws_free(self._handle)
        self._handle = None
        self._closed = True

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            msg = await self.recv(timeout=30.0)
            if msg.is_close:
                raise StopAsyncIteration
            return msg
        except SwpreqError:
            raise StopAsyncIteration


WebSocket = AsyncWebSocket