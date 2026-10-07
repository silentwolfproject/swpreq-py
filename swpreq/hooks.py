from typing import Any, Callable, List

from .response import Response


class Hooks:
    def __init__(self):
        self._request_hooks: List[Callable] = []
        self._response_hooks: List[Callable] = []

    def register_request(self, fn: Callable[[dict], dict]) -> None:
        self._request_hooks.append(fn)

    def register_response(self, fn: Callable[[Response], Response]) -> None:
        self._response_hooks.append(fn)

    def apply_request(self, request: dict) -> dict:
        for hook in self._request_hooks:
            request = hook(request) or request
        return request

    def apply_response(self, response: Response) -> Response:
        for hook in self._response_hooks:
            response = hook(response) or response
        return response

    def clear(self):
        self._request_hooks.clear()
        self._response_hooks.clear()