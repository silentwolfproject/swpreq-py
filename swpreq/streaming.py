from typing import Any, Iterator, Optional
import json as _json_module
import ctypes

from . import _native
from .exceptions import SwpreqError


class ResponseStream:
    def __init__(self, client_handle, url: str, **kwargs):
        self._client = client_handle
        self._url = url
        self._kwargs = kwargs
        self._chunks = []
        self._closed = False

    def iter_content(self, chunk_size: int = 8192) -> Iterator[bytes]:
        response = self._client._request(
            "GET",
            self._url,
            stream=True,
            **self._kwargs,
        )
        body = response.content
        for i in range(0, len(body), chunk_size):
            yield body[i:i + chunk_size]

    def iter_lines(self) -> Iterator[str]:
        for chunk in self.iter_content():
            for line in chunk.decode("utf-8", errors="replace").splitlines():
                yield line

    def iter_json(self) -> Iterator[Any]:
        buffer = ""
        decoder = _json_module.JSONDecoder()
        for chunk in self.iter_content():
            buffer += chunk.decode("utf-8", errors="replace")
            idx = 0
            while idx < len(buffer):
                try:
                    obj, end = decoder.raw_decode(buffer, idx)
                    yield obj
                    idx = end
                except _json_module.JSONDecodeError:
                    break
            buffer = buffer[idx:]

    def close(self):
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()