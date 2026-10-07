from dataclasses import dataclass
from typing import Iterator, Optional
import threading
import time

from .exceptions import SwpreqError


@dataclass
class SseEvent:
    data: str
    event: Optional[str] = None
    id: Optional[str] = None
    retry: Optional[int] = None

    def json(self):
        import json as _json
        return _json.loads(self.data)

    def __repr__(self):
        return f"SseEvent(event={self.event!r}, data={self.data[:50]!r})"


class SseStream:
    def __init__(self, client, url: str, headers: Optional[dict] = None,
                 timeout: Optional[float] = None):
        self._client = client
        self._url = url
        self._headers = headers or {}
        self._timeout = timeout
        self._closed = False

    def __iter__(self) -> Iterator[SseEvent]:
        hdrs = dict(self._headers)
        hdrs["Accept"] = "text/event-stream"
        hdrs["Cache-Control"] = "no-cache"

        response = self._client.get(
            self._url,
            headers=hdrs,
            timeout=self._timeout,
            stream=True,
        )

        if response.status_code != 200:
            raise SwpreqError(
                f"SSE connection failed: HTTP {response.status_code}"
            )

        buffer = ""
        current_event = None
        current_data = ""
        current_id = None
        current_retry = None

        for line in response.text.splitlines():
            if self._closed:
                return

            line = line.rstrip("\r")

            if line == "":
                if current_data or current_event:
                    event = SseEvent(
                        data=current_data.rstrip("\n"),
                        event=current_event,
                        id=current_id,
                        retry=current_retry,
                    )
                    yield event
                    current_event = None
                    current_data = ""
                continue

            if line.startswith("event:"):
                current_event = line[6:].strip()
            elif line.startswith("data:"):
                data_part = line[5:].lstrip()
                if current_data:
                    current_data += "\n"
                current_data += data_part
            elif line.startswith("id:"):
                current_id = line[3:].strip()
            elif line.startswith("retry:"):
                try:
                    current_retry = int(line[6:].strip())
                except ValueError:
                    pass
            elif line.startswith(":"):
                continue

    def close(self):
        self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()