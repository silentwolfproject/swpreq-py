from ._native import get_lib, get_platform_info, detect_platform
from .client import Client, Session
from .response import Response
from .exceptions import (
    SwpreqError,
    PlatformNotSupportedError,
    CoreLoadError,
    FileLockedError,
    NetworkError,
    TimeoutError,
    InvalidUrlError,
    TlsError,
    ProxyError,
    DecodeError,
    EncodeError,
    NotFoundError,
    HTTPError,
)
from .sync_api import get, post, put, delete, patch, head, options, request
from .streaming import ResponseStream
from .sse import SseStream, SseEvent
from .multipart import MultipartBuilder
from .retry import RetryPolicy
from .oauth import OAuth1, OAuth1Params, OAuth2
from .websocket import WebSocket, AsyncWebSocket, WebSocketMessage

__version__ = "0.1.0"

__all__ = [
    "Client",
    "Session",
    "Response",
    "ResponseStream",
    "SseStream",
    "SseEvent",
    "MultipartBuilder",
    "RetryPolicy",
    "OAuth1",
    "OAuth1Params",
    "OAuth2",
    "WebSocket",
    "AsyncWebSocket",
    "WebSocketMessage",
    "SwpreqError",
    "PlatformNotSupportedError",
    "CoreLoadError",
    "FileLockedError",
    "NetworkError",
    "TimeoutError",
    "InvalidUrlError",
    "TlsError",
    "ProxyError",
    "DecodeError",
    "EncodeError",
    "NotFoundError",
    "HTTPError",
    "get",
    "post",
    "put",
    "delete",
    "patch",
    "head",
    "options",
    "request",
    "get_lib",
    "get_platform_info",
    "detect_platform",
]


def __getattr__(name):
    if name == "AsyncClient":
        from .async_api import AsyncClient

        return AsyncClient
    if name == "AsyncSession":
        from .async_api import AsyncSession

        return AsyncSession
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")