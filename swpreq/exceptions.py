class SwpreqError(Exception):
    pass


class PlatformNotSupportedError(SwpreqError):
    pass


class CoreLoadError(SwpreqError):
    pass


class FileLockedError(SwpreqError):
    pass


class NetworkError(SwpreqError):
    pass


class TimeoutError(SwpreqError):
    pass


class InvalidUrlError(SwpreqError):
    pass


class TlsError(SwpreqError):
    pass


class ProxyError(SwpreqError):
    pass


class DecodeError(SwpreqError):
    pass


class EncodeError(SwpreqError):
    pass


class NotFoundError(SwpreqError):
    pass

class AuthError(SwpreqError):
    pass

class InvalidArgumentError(SwpreqError):
    pass

class IOError(SwpreqError):
    pass


class HTTPError(SwpreqError):
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


_ERROR_MAP = {
    1: NetworkError,
    2: TimeoutError,
    3: InvalidUrlError,
    4: TlsError,
    5: ProxyError,
    6: DecodeError,
    7: EncodeError,
    8: SwpreqError,
    9: SwpreqError,
    10: NotFoundError,
    11: AuthError,
    99: SwpreqError,
}


def raise_for_code(code, message):
    cls = _ERROR_MAP.get(code, SwpreqError)
    raise cls(f"[{code}] {message}")