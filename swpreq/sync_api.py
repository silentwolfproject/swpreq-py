from typing import Optional

from .client import Client

_default_client: Optional[Client] = None


def _client() -> Client:
    global _default_client
    if _default_client is None:
        _default_client = Client()
    return _default_client


def get(url: str, **kw):
    return _client().get(url, **kw)


def post(url: str, **kw):
    return _client().post(url, **kw)


def put(url: str, **kw):
    return _client().put(url, **kw)


def delete(url: str, **kw):
    return _client().delete(url, **kw)


def patch(url: str, **kw):
    return _client().patch(url, **kw)


def head(url: str, **kw):
    return _client().head(url, **kw)


def options(url: str, **kw):
    return _client().options(url, **kw)


def request(method: str, url: str, **kw):
    return _client().request(method, url, **kw)