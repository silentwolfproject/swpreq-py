import mimetypes
import os
import uuid
from typing import Any, Dict, List, Optional, Tuple


class MultipartBuilder:
    def __init__(self):
        self._fields: List[Tuple[str, Any]] = []
        self._files: List[Dict[str, Any]] = []
        self._boundary = f"----swpreq-{uuid.uuid4().hex}"

    def text(self, name: str, value: str) -> "MultipartBuilder":
        self._fields.append((name, value))
        return self

    def bytes(
        self,
        name: str,
        data: bytes,
        filename: str,
        mime: Optional[str] = None,
    ) -> "MultipartBuilder":
        mime = mime or "application/octet-stream"
        self._files.append({
            "name": name,
            "data": data,
            "filename": filename,
            "mime": mime,
        })
        return self

    def file(self, name: str, path: str) -> "MultipartBuilder":
        if not os.path.isfile(path):
            raise FileNotFoundError(path)

        with open(path, "rb") as f:
            data = f.read()

        filename = os.path.basename(path)
        mime, _ = mimetypes.guess_type(path)
        mime = mime or "application/octet-stream"

        self._files.append({
            "name": name,
            "data": data,
            "filename": filename,
            "mime": mime,
        })
        return self

    def build(self) -> Tuple[str, bytes]:
        parts = []

        for name, value in self._fields:
            parts.append(f"--{self._boundary}\r\n".encode())
            parts.append(
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
            )
            parts.append(str(value).encode("utf-8"))
            parts.append(b"\r\n")

        for file_info in self._files:
            parts.append(f"--{self._boundary}\r\n".encode())
            parts.append(
                (
                    f'Content-Disposition: form-data; name="{file_info["name"]}"; '
                    f'filename="{file_info["filename"]}"\r\n'
                ).encode()
            )
            parts.append(
                f'Content-Type: {file_info["mime"]}\r\n\r\n'.encode()
            )
            parts.append(file_info["data"])
            parts.append(b"\r\n")

        parts.append(f"--{self._boundary}--\r\n".encode())

        content_type = f"multipart/form-data; boundary={self._boundary}"
        return content_type, b"".join(parts)

    def __len__(self) -> int:
        return len(self._fields) + len(self._files)