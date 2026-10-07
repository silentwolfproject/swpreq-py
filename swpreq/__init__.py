from ._native import get_lib, get_platform_info, detect_platform
from .client import Client, Session
from .async_api import AsyncClient, AsyncSession
from .response import Response
from .exceptions import (
    SwpreqError,
    NetworkError,
    TimeoutError,
    InvalidUrlError,
    TlsError,
    ProxyError,
    DecodeError,
    EncodeError,
    IOError,
    InvalidArgumentError,
    NotFoundError,
    HTTPError,
    PlatformNotSupportedError,
    CoreLoadError,
    FileLockedError,
)
from .sync_api import get, post, put, delete, patch, head, options, request
from .streaming import ResponseStream
from .sse import SseStream, SseEvent
from .multipart import MultipartBuilder
from .retry import RetryPolicy
from .oauth import OAuth1, OAuth1Params, OAuth2
from .websocket import WebSocket, AsyncWebSocket, WebSocketMessage
from .auth import DigestAuth
from .connector import TCPConnector, AsyncResolver, UnixConnector
from .trace import TraceConfig, TraceContext
from .server import AsyncServer, Request, Response as ServerResponse
from .signals import SignalHandler

__version__ = "0.2.0"

__all__ = [
    "Client", "Session", "AsyncClient", "AsyncSession",
    "Response", "ResponseStream", "SseStream", "SseEvent",
    "MultipartBuilder", "RetryPolicy", "OAuth1", "OAuth1Params", "OAuth2",
    "DigestAuth", "WebSocket", "AsyncWebSocket", "WebSocketMessage",
    "TCPConnector", "AsyncResolver", "UnixConnector",
    "TraceConfig", "TraceContext", "AsyncServer", "Request", "ServerResponse",
    "SignalHandler",
    "SwpreqError", "PlatformNotSupportedError", "CoreLoadError", "FileLockedError",
    "NetworkError", "TimeoutError", "InvalidUrlError", "TlsError", "ProxyError",
    "DecodeError", "EncodeError", "NotFoundError", "HTTPError", "AuthError",
    "get", "post", "put", "delete", "patch", "head", "options", "request",
    "get_lib", "get_platform_info", "detect_platform",
]