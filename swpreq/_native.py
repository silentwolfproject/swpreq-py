import ctypes
import ctypes.util
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

from .exceptions import (
    PlatformNotSupportedError,
    CoreLoadError,
    FileLockedError,
)


SUPPORTED_PLATFORMS = {
    ("windows", "x64"): "swpreq.dll",
    ("windows", "arm64"): "swpreq.dll",
    ("linux", "x64"): "libswpreq.so",
    ("linux", "arm64"): "libswpreq.so",
    ("linux", "armv7"): "libswpreq.so",
    ("macos", "x64"): "libswpreq.dylib",
    ("macos", "arm64"): "libswpreq.dylib",
    ("android", "arm64"): "libswpreq.so",
    ("android", "armv7"): "libswpreq.so",
    ("android", "x64"): "libswpreq.so",
    ("android", "x86"): "libswpreq.so",
}


def _detect_android() -> bool:
    if "ANDROID_ROOT" in os.environ:
        return True
    if "ANDROID_DATA" in os.environ:
        return True
    if os.path.exists("/system/build.prop"):
        return True
    try:
        return "android" in platform.platform().lower()
    except Exception:
        return False


def _detect_macos_arch() -> str:
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64"):
        try:
            result = subprocess.run(
                ["sysctl", "-n", "sysctl.proc_translated"],
                capture_output=True,
                text=True,
                timeout=1,
            )
            if result.returncode == 0 and result.stdout.strip() == "1":
                return "arm64"
        except Exception:
            pass
    return machine


def detect_platform() -> tuple:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        os_name = "windows"
    elif system == "darwin":
        os_name = "macos"
        machine = _detect_macos_arch()
    elif system == "linux":
        os_name = "android" if _detect_android() else "linux"
    else:
        os_name = system

    if machine in ("x86_64", "amd64"):
        arch = "x64"
    elif machine in ("aarch64", "arm64"):
        arch = "arm64"
    elif machine in ("armv7l", "armv6l", "armv8l"):
        arch = "armv7"
    elif machine in ("i386", "i686", "x86"):
        arch = "x86"
    else:
        arch = machine

    return os_name, arch


def find_library() -> str:
    os_name, arch = detect_platform()
    key = (os_name, arch)

    if key not in SUPPORTED_PLATFORMS:
        supported = ", ".join(f"{o}-{a}" for o, a in sorted(SUPPORTED_PLATFORMS))
        raise PlatformNotSupportedError(
            f"Platform '{os_name}-{arch}' is not supported.\n"
            f"Supported: {supported}"
        )

    lib_name = SUPPORTED_PLATFORMS[key]
    pkg_dir = Path(__file__).parent

    candidates = [
        pkg_dir / "lib" / f"{os_name}-{arch}" / lib_name,
        pkg_dir / lib_name,
        pkg_dir.parent.parent / "target" / "release" / lib_name,
        pkg_dir.parent.parent / "target" / "debug" / lib_name,
    ]

    for c in candidates:
        if c.exists():
            return str(c)

    tried = "\n".join(f"  - {c}" for c in candidates)
    raise CoreLoadError(
        f"Binary not found for {os_name}-{arch}.\n"
        f"Expected: {lib_name}\n"
        f"Tried:\n{tried}"
    )


class SwpreqResponse(ctypes.Structure):
    _fields_ = [
        ("status_code", ctypes.c_uint16),
        ("_pad", ctypes.c_uint16),
        ("body", ctypes.POINTER(ctypes.c_uint8)),
        ("body_len", ctypes.c_size_t),
        ("headers_json", ctypes.c_char_p),
        ("url", ctypes.c_char_p),
        ("error", ctypes.c_char_p),
        ("elapsed_ms", ctypes.c_uint64),
        ("http_version", ctypes.c_uint32),
    ]


ON_MESSAGE_CB = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.POINTER(ctypes.c_uint8),
    ctypes.c_size_t,
)

ON_EVENT_CB = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_char_p,
)


class CoreLib:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._load()
        return cls._instance

    def __getattr__(self, name):
        # Delegate unknown attributes to the raw CDLL
        # so that client.py can call lib.swpreq_client_new() etc.
        lib = self.__dict__.get("lib")
        if lib is not None:
            return getattr(lib, name)
        raise AttributeError(f"CoreLib has no attribute '{name}'")

    def _load(self) -> None:
        lib_path = find_library()

        try:
            self.lib = ctypes.CDLL(lib_path)
        except OSError:
            try:
                tmp_dir = Path(tempfile.gettempdir()) / "swpreq_lib"
                tmp_dir.mkdir(parents=True, exist_ok=True)
                tmp_path = tmp_dir / f"{os.getpid()}_{Path(lib_path).name}"
                shutil.copy2(lib_path, tmp_path)
                self.lib = ctypes.CDLL(str(tmp_path))
            except OSError as e2:
                raise FileLockedError(f"Failed to load library: {e2}")

        self._setup_signatures()

    def _setup_signatures(self) -> None:
        lib = self.lib

        # Version + memory
        lib.swpreq_version.restype = ctypes.c_char_p
        lib.swpreq_version.argtypes = []

        lib.swpreq_string_free.restype = None
        lib.swpreq_string_free.argtypes = [ctypes.c_char_p]

        lib.swpreq_response_free.restype = None
        lib.swpreq_response_free.argtypes = [ctypes.POINTER(SwpreqResponse)]

        # Client
        lib.swpreq_client_new.restype = ctypes.c_void_p
        lib.swpreq_client_new.argtypes = [ctypes.c_char_p]

        lib.swpreq_client_free.restype = None
        lib.swpreq_client_free.argtypes = [ctypes.c_void_p]

        # Headers + cookies
        lib.swpreq_set_default_header.restype = ctypes.c_int
        lib.swpreq_set_default_header.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        lib.swpreq_remove_default_header.restype = ctypes.c_int
        lib.swpreq_remove_default_header.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
        ]

        lib.swpreq_clear_default_headers.restype = ctypes.c_int
        lib.swpreq_clear_default_headers.argtypes = [ctypes.c_void_p]

        lib.swpreq_set_cookie.restype = ctypes.c_int
        lib.swpreq_set_cookie.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
        ]

        lib.swpreq_clear_cookies.restype = ctypes.c_int
        lib.swpreq_clear_cookies.argtypes = [ctypes.c_void_p]

        # Request
        lib.swpreq_request_sync.restype = ctypes.POINTER(SwpreqResponse)
        lib.swpreq_request_sync.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_uint8),
            ctypes.c_size_t,
            ctypes.c_uint64,
            ctypes.c_char_p,
            ctypes.c_int64,
            ctypes.c_int,
        ]

        # Retry (optional)
        if hasattr(lib, "swpreq_client_set_retry"):
            lib.swpreq_client_set_retry.restype = ctypes.c_int
            lib.swpreq_client_set_retry.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint32,
                ctypes.c_uint64,
                ctypes.c_int,
                ctypes.c_int,
            ]

        # WebSocket (optional)
        if hasattr(lib, "swpreq_ws_connect"):
            lib.swpreq_ws_connect.restype = ctypes.c_int
            lib.swpreq_ws_connect.argtypes = [
                ctypes.c_char_p,
                ctypes.c_char_p,
                ctypes.POINTER(ctypes.c_int),
                ctypes.POINTER(ctypes.c_char_p),
            ]

            lib.swpreq_ws_set_callbacks.restype = ctypes.c_int
            lib.swpreq_ws_set_callbacks.argtypes = [
                ctypes.c_int,
                ctypes.c_void_p, ctypes.c_void_p,
                ctypes.c_void_p, ctypes.c_void_p,
                ctypes.c_void_p, ctypes.c_void_p,
                ctypes.c_void_p, ctypes.c_void_p,
            ]

            lib.swpreq_ws_send_text.restype = ctypes.c_int
            lib.swpreq_ws_send_text.argtypes = [ctypes.c_int, ctypes.c_char_p]

            lib.swpreq_ws_send_binary.restype = ctypes.c_int
            lib.swpreq_ws_send_binary.argtypes = [
                ctypes.c_int,
                ctypes.POINTER(ctypes.c_uint8),
                ctypes.c_size_t,
            ]

            lib.swpreq_ws_send_ping.restype = ctypes.c_int
            lib.swpreq_ws_send_ping.argtypes = [ctypes.c_int]

            lib.swpreq_ws_close.restype = ctypes.c_int
            lib.swpreq_ws_close.argtypes = [ctypes.c_int]

            lib.swpreq_ws_free.restype = None
            lib.swpreq_ws_free.argtypes = [ctypes.c_int]

    def version(self) -> str:
        v = self.lib.swpreq_version()
        if not v:
            return ""
        return v.decode("utf-8")

    def platform_info(self) -> dict:
        os_name, arch = detect_platform()
        return {
            "os": os_name,
            "arch": arch,
            "supported": (os_name, arch) in SUPPORTED_PLATFORMS,
            "library_name": SUPPORTED_PLATFORMS.get((os_name, arch)),
        }


_core_instance: Optional[CoreLib] = None


def get_lib() -> CoreLib:
    global _core_instance
    if _core_instance is None:
        _core_instance = CoreLib()
    return _core_instance


def get_platform_info() -> dict:
    return get_lib().platform_info()