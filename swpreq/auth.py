import base64
import hashlib
import os
import re


class DigestAuth:
    def __init__(self, username, password, algorithm="MD5"):
        self.username = username
        self.password = password
        self.algorithm = algorithm
        self._challenge = None
        self._nc = 0
        self._cnonce = None

    def _parse_challenge(self, header):
        if not header.startswith("Digest"):
            return None

        header = header[6:].strip()
        challenge = {}

        pattern = re.compile(r'(\w+)=(?:"([^"]*)"|([^,\s]+))')
        for match in pattern.finditer(header):
            key = match.group(1).lower()
            value = match.group(2) if match.group(2) is not None else match.group(3)
            challenge[key] = value

        return challenge

    def _hash(self, data):
        algo = self.algorithm.upper()
        if algo in ("MD5", "MD5-SESS"):
            return hashlib.md5(data.encode()).hexdigest()
        if algo in ("SHA-256", "SHA-256-SESS"):
            return hashlib.sha256(data.encode()).hexdigest()
        return hashlib.md5(data.encode()).hexdigest()

    def _generate_cnonce(self):
        return base64.b64encode(os.urandom(16)).decode().rstrip("=")

    def _build_header(self, method, uri):
        if not self._challenge:
            return None

        self._nc += 1
        self._cnonce = self._cnonce or self._generate_cnonce()
        nc_str = f"{self._nc:08x}"

        realm = self._challenge.get("realm", "")
        nonce = self._challenge.get("nonce", "")
        qop = self._challenge.get("qop")
        opaque = self._challenge.get("opaque")

        ha1 = self._hash(f"{self.username}:{realm}:{self.password}")
        ha2 = self._hash(f"{method}:{uri}")

        if qop:
            qop_value = qop.split(",")[0].strip()
            response = self._hash(
                f"{ha1}:{nonce}:{nc_str}:{self._cnonce}:{qop_value}:{ha2}"
            )
        else:
            qop_value = None
            response = self._hash(f"{ha1}:{nonce}:{ha2}")

        parts = [
            f'username="{self.username}"',
            f'realm="{realm}"',
            f'nonce="{nonce}"',
            f'uri="{uri}"',
            f'response="{response}"',
        ]

        if self.algorithm != "MD5":
            parts.append(f"algorithm={self.algorithm}")

        if opaque:
            parts.append(f'opaque="{opaque}"')

        if qop_value:
            parts.append(f"qop={qop_value}")
            parts.append(f"nc={nc_str}")
            parts.append(f'cnonce="{self._cnonce}"')

        return "Digest " + ", ".join(parts)

    def register(self, client):
        self._client = client
        client.register_request_hook(self._request_hook)
        client.register_response_hook(self._response_hook)

    def _request_hook(self, req):
        if self._challenge:
            header = self._build_header(req["method"], req["url"])
            if header:
                req["headers"]["Authorization"] = header
        return req

    def _response_hook(self, res):
        if res.status_code == 401:
            www_auth = res.header("WWW-Authenticate")
            if www_auth and www_auth.startswith("Digest"):
                self._challenge = self._parse_challenge(www_auth)
        return res