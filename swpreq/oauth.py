import base64
import hashlib
import hmac
import os
import time
import urllib.parse
from dataclasses import dataclass
from typing import Dict, Optional

from .exceptions import SwpreqError


@dataclass
class OAuth1Params:
    consumer_key: str
    consumer_secret: str
    token: Optional[str] = None
    token_secret: Optional[str] = None
    signature_method: str = "HMAC-SHA1"
    timestamp: Optional[int] = None
    nonce: Optional[str] = None
    version: str = "1.0"


class OAuth1:
    @staticmethod
    def generate_header(
        params: OAuth1Params,
        method: str,
        url: str,
        extra: Optional[Dict[str, str]] = None,
    ) -> str:
        timestamp = params.timestamp or int(time.time())
        nonce = params.nonce or base64.urlsafe_b64encode(
            os.urandom(16)
        ).decode().rstrip("=")

        oauth_params = {
            "oauth_consumer_key": params.consumer_key,
            "oauth_nonce": nonce,
            "oauth_signature_method": params.signature_method,
            "oauth_timestamp": str(timestamp),
            "oauth_version": params.version,
        }

        if params.token:
            oauth_params["oauth_token"] = params.token

        if extra:
            oauth_params.update(extra)

        signature = OAuth1._compute_signature(
            method,
            url,
            oauth_params,
            params.consumer_secret,
            params.token_secret,
        )

        oauth_params["oauth_signature"] = signature

        parts = [
            f'{OAuth1._url_encode(k)}="{OAuth1._url_encode(v)}"'
            for k, v in sorted(oauth_params.items())
        ]

        return "OAuth " + ", ".join(parts)

    @staticmethod
    def _compute_signature(
        method: str,
        url: str,
        params: Dict[str, str],
        consumer_secret: str,
        token_secret: Optional[str],
    ) -> str:
        sorted_params = sorted(params.items())
        param_string = "&".join(
            f"{OAuth1._url_encode(k)}={OAuth1._url_encode(v)}"
            for k, v in sorted_params
        )

        base_string = "&".join([
            method.upper(),
            OAuth1._url_encode(url),
            OAuth1._url_encode(param_string),
        ])

        signing_key = "&".join([
            OAuth1._url_encode(consumer_secret),
            OAuth1._url_encode(token_secret or ""),
        ])

        signature = hmac.new(
            signing_key.encode(),
            base_string.encode(),
            hashlib.sha1,
        ).digest()

        return base64.b64encode(signature).decode()

    @staticmethod
    def _url_encode(value: str) -> str:
        return urllib.parse.quote(str(value), safe="~")


class OAuth2:
    @staticmethod
    def bearer_header(token: str) -> Dict[str, str]:
        return {"Authorization": f"Bearer {token}"}

    @staticmethod
    def client_credentials(
        token_url: str,
        client_id: str,
        client_secret: str,
        scope: Optional[str] = None,
        timeout: float = 30.0,
    ) -> Dict[str, str]:
        from .sync_api import post as _post

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }
        if scope:
            data["scope"] = scope

        r = _post(token_url, data=data, timeout=timeout)
        if r.status_code != 200:
            raise SwpreqError(
                f"OAuth2 token request failed: HTTP {r.status_code}"
            )

        body = r.json()
        return {
            "access_token": body["access_token"],
            "token_type": body.get("token_type", "Bearer"),
            "expires_in": body.get("expires_in"),
            "refresh_token": body.get("refresh_token"),
        }