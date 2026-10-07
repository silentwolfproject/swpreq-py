<div align="center">

<img src="https://raw.githubusercontent.com/silentwolfproject/swpreq-py/main/assets/banner.png" alt="swpreq" width="100%" />

# swpreq

**High-performance HTTP client for Python with a Rust core.**

Up to **21.10x faster than `requests`** in the tested asynchronous concurrent workload.

[![PyPI](https://img.shields.io/badge/version-0.1.0-orange?style=for-the-badge)](https://pypi.org/project/swpreq/)
[![Python](https://img.shields.io/badge/Python-Compatible-blue?style=for-the-badge)](https://pypi.org/project/swpreq/)
[![License](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Cross--Platform-purple?style=for-the-badge)](https://pypi.org/project/swpreq/)

[Installation](#installation) ·
[Quick Start](#quick-start) ·
[Features](#features) ·
[Examples](#examples) ·
[Benchmark](#benchmark) ·
[API Reference](#api-reference)

</div>

---

## About

`swpreq` is a Python HTTP client powered by a native Rust core.

It provides synchronous and asynchronous APIs for HTTP communication while supporting HTTP/1.1, HTTP/2, WebSocket, SSE, streaming, multipart requests, authentication helpers, retries, hooks, proxies, cookies, and more.

The Python layer provides the public API while request processing is handled by the native core.

### Core Design

* Native Rust HTTP implementation
* Thin Python interface through C ABI
* Synchronous and asynchronous APIs
* HTTP/1.1 and HTTP/2 support
* Native connection management
* TLS handled by the Rust core
* Native async concurrency
* Prebuilt binaries for supported platforms

The native library is loaded through a thin Python wrapper using `ctypes`.

---

## Installation

Install from PyPI:

```bash
pip install swpreq
```

Prebuilt binaries are included for supported platforms, so a Rust toolchain is not required for normal installation.

---

# Quick Start

## Basic Request

The simplest way to make an HTTP request is through the module-level API.

```python
import swpreq

response = swpreq.get("https://httpbin.org/get")

print(response.status_code)
print(response.json())
```

The returned `Response` object provides access to the HTTP status, headers, body, URL, timing information, and other response data.

## Request Parameters

Query parameters and headers can be passed directly to the request.

```python
import swpreq

response = swpreq.get(
    "https://httpbin.org/get",
    params={
        "name": "name123",
        "age": 25,
    },
    headers={
        "X-Custom": "hello",
    },
)

print(response.json()["args"])
```

## JSON Request

HTTP methods that send data can use the `json` parameter.

```python
import swpreq

response = swpreq.post(
    "https://httpbin.org/post",
    json={
        "name": "name123",
        "age": 25,
    },
)

print(response.status_code)
print(response.json())
```

## Reusable Client

Use `Client` when multiple requests should share configuration such as headers, cookies, retry policies, or connection state.

```python
from swpreq import Client

with Client() as client:
    client.set_header(
        "Authorization",
        "Bearer token",
    )

    response = client.get(
        "https://httpbin.org/headers"
    )

    print(response.status_code)
```

## Asynchronous Requests

Use `AsyncClient` when requests need to run asynchronously.

```python
import asyncio
from swpreq import AsyncClient

async def main():
    async with AsyncClient() as client:
        response = await client.get(
            "https://httpbin.org/get"
        )

        print(response.status_code)

asyncio.run(main())
```

This is the basic API. More advanced capabilities are covered in [Examples](#examples).

---

# Core Features

| Feature             | Description                                        |
| ------------------- | -------------------------------------------------- |
| HTTP/1.1            | Keep-alive and chunked transfer support            |
| HTTP/2              | Multiplexing and header compression                |
| Sync API            | `Client`, `Session`, and module-level requests     |
| Async API           | `AsyncClient`, `AsyncSession`, `map`, and `gather` |
| WebSocket           | Full-duplex communication                          |
| SSE                 | Server-Sent Events with reconnect support          |
| Streaming           | Content, line, and JSON iterators                  |
| Multipart           | Text, bytes, and file uploads                      |
| OAuth               | OAuth 1.0a and OAuth 2.0 helpers                   |
| Retry               | Retry policies, exponential backoff, and jitter    |
| Hooks               | Request and response hooks                         |
| Cookies             | Cookie storage and per-domain handling             |
| Proxy               | HTTP, HTTPS, SOCKS4, and SOCKS5                    |
| Redirects           | Configurable redirect handling                     |
| Timeout             | Per-request and per-client timeouts                |
| Compression         | gzip, brotli, zstd, and deflate                    |
| TLS                 | Rustls with TLS 1.3                                |
| Netrc               | `.netrc` authentication lookup                     |
| Adapter             | Mount custom clients to URL prefixes               |
| Multi-language Core | Native C ABI for future integrations               |

---

# Response

Every request returns a `Response` object.

```python
import swpreq

response = swpreq.get(
    "https://httpbin.org/json"
)

print(response.status_code)
print(response.text)
```

Common properties include:

```python
response.status_code
response.ok
response.is_success
response.is_redirect
response.is_client_error
response.is_server_error

response.headers
response.cookies
response.links

response.content
response.text
response.encoding

response.url
response.http_version
response.elapsed_ms
response.history
response.request_id
```

Response helpers include:

```python
response.json()
response.header("Content-Type")
response.cookie("session")
response.link("next")
response.next_page_url()
response.iter_content(1024)
response.raise_for_status()
```

---

# HTTP Methods

`swpreq` provides the common HTTP methods directly:

```python
import swpreq

swpreq.get("https://httpbin.org/get")

swpreq.post(
    "https://httpbin.org/post",
    json={"name": "name123"},
)

swpreq.put(
    "https://httpbin.org/put",
    json={"updated": True},
)

swpreq.patch(
    "https://httpbin.org/patch",
    json={"patched": True},
)

swpreq.delete(
    "https://httpbin.org/delete"
)

swpreq.head(
    "https://httpbin.org/get"
)

swpreq.options(
    "https://httpbin.org/get"
)

swpreq.request(
    "GET",
    "https://httpbin.org/get"
)
```

---

# Client and Session

For applications that make multiple requests, `Client` provides reusable configuration.

```python
from swpreq import Client

with Client() as client:

    client.set_header(
        "Authorization",
        "Bearer token",
    )

    client.set_cookie(
        "session",
        "xyz789",
        ".httpbin.org",
    )

    first = client.get(
        "https://httpbin.org/headers"
    )

    second = client.get(
        "https://httpbin.org/cookies"
    )
```

Headers can also be managed directly:

```python
client.set_header("X-App-Version", "1.0.0")

client.update_headers({
    "X-Platform": "desktop",
    "X-Client": "swpreq",
})

client.remove_header("X-Client")

client.clear_headers()
```

---

# Asynchronous API

`AsyncClient` provides asynchronous requests and concurrent execution.

## Concurrent Requests

```python
import asyncio
from swpreq import AsyncClient

async def main():

    async with AsyncClient(
        max_workers=32
    ) as client:

        urls = [
            f"https://httpbin.org/get?i={i}"
            for i in range(100)
        ]

        results = await client.map(urls)

        successful = sum(
            1
            for response in results
            if response.is_success
        )

        print(
            f"{successful}/100 succeeded"
        )

asyncio.run(main())
```

## Gather

Multiple asynchronous requests can also be gathered together.

```python
import asyncio
from swpreq import AsyncClient

async def main():

    async with AsyncClient() as client:

        r1, r2, r3 = await client.gather(
            client.get(
                "https://httpbin.org/get?x=1"
            ),
            client.get(
                "https://httpbin.org/get?x=2"
            ),
            client.get(
                "https://httpbin.org/get?x=3"
            ),
        )

        print(r1.json()["args"]["x"])
        print(r2.json()["args"]["x"])
        print(r3.json()["args"]["x"])

asyncio.run(main())
```

---

# Timeouts

Timeouts can be configured per request.

```python
import swpreq

response = swpreq.get(
    "https://httpbin.org/delay/1",
    timeout=30.0,
)
```

Timeout errors can be handled explicitly:

```python
import swpreq

try:
    response = swpreq.get(
        "https://httpbin.org/delay/10",
        timeout=1.0,
    )

except swpreq.TimeoutError:
    print("Request timed out")
```

---

# Retry Policy

Retry behavior can be configured through `RetryPolicy`.

```python
from swpreq import Client, RetryPolicy

with Client(
    retry=RetryPolicy.aggressive()
) as client:

    response = client.get(
        "https://httpbin.org/get"
    )
```

Disable retries:

```python
with Client(
    retry=RetryPolicy.none()
) as client:

    response = client.get(
        "https://httpbin.org/get"
    )
```

Custom policy:

```python
policy = RetryPolicy(
    max_retries=5,
    base_delay_ms=200,
    exponential=True,
    jitter=True,
)

with Client(retry=policy) as client:
    response = client.get(
        "https://httpbin.org/get"
    )
```

---

# Redirects

Redirect handling is configurable.

```python
import swpreq

response = swpreq.get(
    "https://httpbin.org/redirect/3"
)
```

Disable redirects:

```python
response = swpreq.get(
    "https://httpbin.org/redirect/1",
    allow_redirects=False,
)

print(response.status_code)
```

Set a redirect limit:

```python
response = swpreq.get(
    "https://httpbin.org/redirect/10",
    max_redirects=3,
)
```

---

# Streaming

Responses can be processed incrementally instead of loading everything at once.

```python
from swpreq import Client

with Client() as client:

    stream = client.stream(
        "GET",
        "https://httpbin.org/stream/5",
    )

    for chunk in stream.iter_content(512):
        print(len(chunk))
```

Streaming helpers include:

```python
stream.iter_content(...)
stream.iter_lines(...)
stream.iter_json(...)
```

---

# Multipart

Multipart requests support text fields, bytes, and files.

```python
from swpreq import Client, MultipartBuilder

with Client() as client:

    multipart = (
        MultipartBuilder()
        .text("name", "name123")
        .text("age", "25")
        .bytes(
            "avatar",
            b"content",
            "avatar.bin",
            "application/octet-stream",
        )
        .file(
            "document",
            "./report.pdf",
        )
    )

    response = client.post(
        "https://httpbin.org/post",
        files=multipart,
    )

    print(response.json())
```

---

# Authentication

## OAuth 1.0

```python
from swpreq import OAuth1, OAuth1Params

params = OAuth1Params(
    consumer_key="key",
    consumer_secret="secret",
    token="token",
    token_secret="token-secret",
)

header = OAuth1.generate_header(
    params,
    "GET",
    "https://api.example.com/data",
)

print(header)
```

## OAuth 2.0

Bearer authentication:

```python
from swpreq import OAuth2

headers = OAuth2.bearer_header(
    "my-token"
)
```

Client credentials:

```python
token = OAuth2.client_credentials(
    token_url="https://api.example.com/oauth/token",
    client_id="client-id",
    client_secret="client-secret",
    scope="read write",
)
```

---

# Hooks

Request and response hooks can be registered on a client.

```python
from swpreq import Client

with Client() as client:

    def request_hook(request):
        request["headers"]["X-Hook"] = "yes"
        return request

    def response_hook(response):
        print(
            f"Received {response.status_code}"
            f" from {response.url}"
        )
        return response

    client.register_request_hook(
        request_hook
    )

    client.register_response_hook(
        response_hook
    )

    response = client.get(
        "https://httpbin.org/headers"
    )
```

---

# WebSocket

WebSocket communication is available through `AsyncWebSocket`.

```python
import asyncio
from swpreq import AsyncWebSocket

async def main():

    async with AsyncWebSocket(
        "wss://echo.websocket.events"
    ) as websocket:

        await websocket.send_text(
            "Hello"
        )

        message = await websocket.recv(
            timeout=5.0
        )

        print(message.data)

asyncio.run(main())
```

Callback-based handling is also supported:

```python
import asyncio
from swpreq import AsyncWebSocket

async def main():

    websocket = AsyncWebSocket(
        "wss://echo.websocket.events"
    )

    websocket.on_open(
        lambda: print("connected")
    )

    websocket.on_message(
        lambda message: print(
            f"received: {message.data}"
        )
    )

    websocket.on_close(
        lambda code, reason: print(
            f"closed: {code}"
        )
    )

    websocket.on_error(
        lambda error: print(
            f"error: {error}"
        )
    )

    await websocket.connect()

    await websocket.send_text(
        "Hello"
    )

    await websocket.send_json({
        "hello": "world"
    })

    await websocket.send_binary(
        b"binary data"
    )

    await asyncio.sleep(2)

    await websocket.close()

asyncio.run(main())
```

---

# SSE

Server-Sent Events are available through the client streaming interface.

```python
from swpreq import Client

with Client() as client:

    stream = client.sse(
        "https://example.com/events"
    )

    for event in stream:
        print(event)
```

---

# Examples

The following examples focus on practical implementations rather than individual source files.

## Basic API Client

```python
import swpreq

response = swpreq.get(
    "https://api.example.com/users",
    headers={
        "Authorization": "Bearer TOKEN",
    },
    params={
        "page": 1,
        "limit": 20,
    },
)

response.raise_for_status()

users = response.json()

for user in users:
    print(user)
```

## Reusable API Service

```python
from swpreq import Client

class API:

    def __init__(self, token):
        self.client = Client()

        self.client.set_header(
            "Authorization",
            f"Bearer {token}",
        )

    def users(self):
        response = self.client.get(
            "https://api.example.com/users"
        )

        response.raise_for_status()

        return response.json()

    def close(self):
        self.client.close()


api = API("TOKEN")

try:
    users = api.users()

    for user in users:
        print(user)

finally:
    api.close()
```

## Concurrent API Requests

```python
import asyncio
from swpreq import AsyncClient

async def fetch_users():

    urls = [
        f"https://api.example.com/users/{i}"
        for i in range(1, 101)
    ]

    async with AsyncClient(
        max_workers=32
    ) as client:

        responses = await client.map(
            urls
        )

        return [
            response.json()
            for response in responses
            if response.is_success
        ]


users = asyncio.run(
    fetch_users()
)

print(
    f"Received {len(users)} users"
)
```

## Downloading a Large Response

```python
from swpreq import Client

with Client() as client:

    stream = client.stream(
        "GET",
        "https://example.com/large-file.zip",
    )

    with open(
        "large-file.zip",
        "wb",
    ) as file:

        for chunk in stream.iter_content(
            64 * 1024
        ):
            file.write(chunk)
```

## Uploading a File

```python
from swpreq import Client, MultipartBuilder

with Client() as client:

    multipart = (
        MultipartBuilder()
        .text("description", "Example document")
        .file(
            "document",
            "./document.pdf",
        )
    )

    response = client.post(
        "https://api.example.com/upload",
        files=multipart,
    )

    response.raise_for_status()

    print(response.json())
```

## Handling HTTP and Network Errors

```python
import swpreq

try:

    response = swpreq.get(
        "https://api.example.com/data",
        timeout=10,
    )

    response.raise_for_status()

except swpreq.TimeoutError:
    print("Request timed out")

except swpreq.NetworkError:
    print("Network error")

except swpreq.HTTPError as error:
    print(
        f"HTTP error: {error.status_code}"
    )

except swpreq.SwpreqError as error:
    print(
        f"swpreq error: {error}"
    )
```

## Mounting a Custom Client

```python
from swpreq import Client

with Client() as main:

    with Client(
        user_agent="SubClient/1.0"
    ) as sub:

        main.mount(
            "https://api.example.com/",
            sub,
        )

        response = main.get(
            "https://api.example.com/data"
        )

        print(response.status_code)
```

## Platform Detection

```python
import swpreq

platform = swpreq.get_platform_info()

print("OS:", platform["os"])
print("Architecture:", platform["arch"])
print("Supported:", platform["supported"])
print("Library:", platform["library_name"])
```

---

# Benchmark

Performance figures below are from direct tests performed against the listed targets and environments.

They should be interpreted as **benchmark results for the tested workloads**, not as a universal guarantee for every network, server, payload, or hardware configuration.

## Test Environment

* OS: Windows 11
* Python: 3.10
* Remote target: `httpbin.org`
* Approximate remote latency: 500 ms
* Local target: localhost

## swpreq vs requests

| Scenario                           | requests | swpreq |    Speedup |
| ---------------------------------- | -------: | -----: | ---------: |
| Sequential remote, 50 requests     |   53.61s | 14.33s |  **3.74x** |
| Sequential localhost, 500 requests |    4.85s |  3.43s |  **1.41x** |
| Async concurrent, 50 requests      |   14.31s |  2.12s |  **6.75x** |
| Async concurrent, 100 requests     |   29.60s |  2.00s | **14.79x** |
| Async concurrent, 200 requests     |   61.98s |  2.94s | **21.10x** |

The highest measured difference in this test was **21.10x** for 200 concurrent requests.

## swpreq vs aiohttp

| Scenario                      | aiohttp | swpreq |   Speedup |
| ----------------------------- | ------: | -----: | --------: |
| Remote, 50 requests           |   1.74s |  1.68s | **1.04x** |
| Remote, 100 requests          |   2.10s |  2.00s | **1.05x** |
| Remote, 200 requests          |   2.62s |  3.04s | **0.86x** |
| Remote JSON API, 100 requests |   0.64s |  0.30s | **2.17x** |
| Worker = 128                  |   1.83s |  1.46s | **1.26x** |
| Localhost, 500 requests       |   8.20s |  4.50s | **1.82x** |

The results show that performance depends on the workload. `swpreq` was faster in most of the tested scenarios, but it was not faster in every test.

## Implementation Differences

The native architecture allows several parts of the HTTP stack to run outside the Python layer.

| Layer               | requests           | swpreq                         |
| ------------------- | ------------------ | ------------------------------ |
| HTTP client         | urllib3            | reqwest                        |
| TLS                 | OpenSSL via Python | rustls                         |
| JSON processing     | Python             | Rust                           |
| Compression         | Python             | Rust                           |
| Connection handling | Python layer       | Rust core                      |
| Concurrency         | Blocking / manual  | Native async                   |
| GIL                 | Python execution   | Core processing outside Python |

These architectural differences are relevant to the benchmark results, particularly for workloads involving concurrent requests and network I/O.

---

# API Reference

## Module-Level Functions

| Function           | Parameters              | Returns    | Description        |
| ------------------ | ----------------------- | ---------- | ------------------ |
| `swpreq.get()`     | `url, **kwargs`         | `Response` | HTTP GET           |
| `swpreq.post()`    | `url, **kwargs`         | `Response` | HTTP POST          |
| `swpreq.put()`     | `url, **kwargs`         | `Response` | HTTP PUT           |
| `swpreq.patch()`   | `url, **kwargs`         | `Response` | HTTP PATCH         |
| `swpreq.delete()`  | `url, **kwargs`         | `Response` | HTTP DELETE        |
| `swpreq.head()`    | `url, **kwargs`         | `Response` | HTTP HEAD          |
| `swpreq.options()` | `url, **kwargs`         | `Response` | HTTP OPTIONS       |
| `swpreq.request()` | `method, url, **kwargs` | `Response` | Custom HTTP method |

## Request Parameters

| Parameter         | Type                   | Default | Description       |
| ----------------- | ---------------------- | ------- | ----------------- |
| `params`          | `dict`                 | `None`  | Query parameters  |
| `headers`         | `dict`                 | `None`  | Request headers   |
| `data`            | `dict \| str \| bytes` | `None`  | Form or raw body  |
| `json`            | `Any`                  | `None`  | JSON request body |
| `body`            | `bytes`                | `None`  | Raw request body  |
| `files`           | `MultipartBuilder`     | `None`  | Multipart upload  |
| `timeout`         | `float`                | `30.0`  | Request timeout   |
| `proxy`           | `str`                  | `None`  | Proxy URL         |
| `allow_redirects` | `bool`                 | `True`  | Follow redirects  |
| `max_redirects`   | `int`                  | `10`    | Maximum redirects |
| `stream`          | `bool`                 | `False` | Enable streaming  |

## Client

| Method                     | Description              |
| -------------------------- | ------------------------ |
| `Client(...)`              | Create a reusable client |
| `get()`                    | GET request              |
| `post()`                   | POST request             |
| `put()`                    | PUT request              |
| `delete()`                 | DELETE request           |
| `patch()`                  | PATCH request            |
| `head()`                   | HEAD request             |
| `options()`                | OPTIONS request          |
| `request()`                | Custom HTTP request      |
| `set_header()`             | Set a default header     |
| `update_headers()`         | Update default headers   |
| `remove_header()`          | Remove a header          |
| `clear_headers()`          | Remove all headers       |
| `set_cookie()`             | Set a cookie             |
| `clear_cookies()`          | Clear cookies            |
| `set_retry()`              | Set retry policy         |
| `mount()`                  | Mount another client     |
| `unmount()`                | Remove mounted client    |
| `register_request_hook()`  | Register request hook    |
| `register_response_hook()` | Register response hook   |
| `stream()`                 | Create streaming request |
| `sse()`                    | Create SSE stream        |
| `multipart()`              | Create multipart builder |
| `close()`                  | Close client             |

## AsyncClient

`AsyncClient` provides the same core request methods asynchronously.

Additional methods:

| Method             | Returns          | Description         |
| ------------------ | ---------------- | ------------------- |
| `await c.get()`    | `Response`       | Async GET           |
| `await c.post()`   | `Response`       | Async POST          |
| `await c.put()`    | `Response`       | Async PUT           |
| `await c.delete()` | `Response`       | Async DELETE        |
| `await c.patch()`  | `Response`       | Async PATCH         |
| `await c.map()`    | `list[Response]` | Concurrent requests |
| `await c.gather()` | `list[Response]` | Gather coroutines   |
| `await c.close()`  | `None`           | Close client        |

## Response

### Properties

| Property           | Type    | Description                |
| ------------------ | ------- | -------------------------- |
| `status_code`      | `int`   | HTTP status                |
| `reason`           | `str`   | Reason phrase              |
| `ok`               | `bool`  | Status below 400           |
| `is_success`       | `bool`  | 2xx response               |
| `is_redirect`      | `bool`  | 3xx response               |
| `is_client_error`  | `bool`  | 4xx response               |
| `is_server_error`  | `bool`  | 5xx response               |
| `headers`          | `dict`  | Response headers           |
| `cookies`          | `dict`  | Response cookies           |
| `links`            | `dict`  | Parsed links               |
| `content`          | `bytes` | Raw response body          |
| `text`             | `str`   | Decoded response body      |
| `encoding`         | `str`   | Response encoding          |
| `url`              | `str`   | Final URL                  |
| `http_version`     | `str`   | HTTP version               |
| `http_version_num` | `int`   | Numeric HTTP version       |
| `elapsed_ms`       | `int`   | Request duration           |
| `history`          | `list`  | Redirect history           |
| `request_id`       | `str`   | Server-provided request ID |

### Methods

| Method               | Returns       | Description             |
| -------------------- | ------------- | ----------------------- |
| `json()`             | `Any`         | Parse JSON              |
| `header(name)`       | `str \| None` | Read header             |
| `cookie(name)`       | `str \| None` | Read cookie             |
| `link(rel)`          | `str \| None` | Read link               |
| `next_page_url()`    | `str \| None` | Get next page URL       |
| `iter_content(n)`    | Iterator      | Iterate response chunks |
| `raise_for_status()` | `None`        | Raise for HTTP errors   |

---

# Output Types

Responses are exposed as native Python types.

| Output           | Type                               |
| ---------------- | ---------------------------------- |
| `status_code`    | `int`                              |
| `headers`        | `dict`                             |
| `cookies`        | `dict`                             |
| `links`          | `dict`                             |
| `content`        | `bytes`                            |
| `text`           | `str`                              |
| `json()`         | `dict`, `list`, or other JSON type |
| `iter_content()` | Iterator of `bytes`                |
| `iter_lines()`   | Iterator of `str`                  |
| `iter_json()`    | Iterator of parsed objects         |

---

# Error Handling

All library exceptions inherit from `SwpreqError`.

| Exception                   |    Code | Description                        |
| --------------------------- | ------: | ---------------------------------- |
| `NetworkError`              |       1 | Network-level error                |
| `TimeoutError`              |       2 | Request timeout                    |
| `InvalidUrlError`           |       3 | Invalid URL                        |
| `TlsError`                  |       4 | TLS handshake failure              |
| `ProxyError`                |       5 | Proxy connection failure           |
| `DecodeError`               |       6 | Response decoding failure          |
| `EncodeError`               |       7 | Request encoding failure           |
| `IOError`                   |       8 | I/O failure                        |
| `InvalidArgumentError`      |       9 | Invalid argument                   |
| `NotFoundError`             |      10 | Resource not found                 |
| `HTTPError`                 | 4xx/5xx | HTTP status error                  |
| `PlatformNotSupportedError` |       — | Unsupported platform               |
| `CoreLoadError`             |       — | Native library could not be loaded |
| `FileLockedError`           |       — | Native library is locked           |

Example:

```python
import swpreq

try:

    response = swpreq.get(
        "https://invalid-url"
    )

    response.raise_for_status()

except swpreq.TimeoutError:
    print("Timeout")

except swpreq.NetworkError:
    print("Network error")

except swpreq.HTTPError as error:
    print(
        f"HTTP {error.status_code}"
    )

except swpreq.SwpreqError as error:
    print(
        f"swpreq error: {error}"
    )
```

---

# Platform Support

| Platform | Architectures          | Status    |
| -------- | ---------------------- | --------- |
| Windows  | x64, arm64, x86        | Supported |
| Linux    | x64, arm64, armv7      | Supported |
| macOS    | x64, arm64             | Supported |
| Android  | arm64, armv7, x64, x86 | Supported |

Prebuilt native binaries are included in the package for supported targets.

No build step is required for normal installation.

---

# Architecture

At a high level, a request follows this path:

```text
Python Application
       |
       v
swpreq Python API
       |
       v
C ABI Boundary
       |
       v
Rust HTTP Core
       |
       +---- URL / Request Processing
       +---- Connection Management
       +---- TLS
       +---- HTTP/1.1
       +---- HTTP/2
       +---- Compression
       +---- Async Execution
       |
       v
Response
       |
       v
Python Response Object
```

The Python API remains responsible for the developer-facing interface while the native core performs the lower-level HTTP processing.

---

# Contributing

Contributions are welcome through the project repository.

The Rust core is currently private. Contributions to the public Python layer and documentation are welcome.

---

# Related Projects

* **swpreq-core** — Native Rust core
* **swpreq-py** — Python interface

---

# License

MIT License.

See [LICENSE](LICENSE) for the complete license text.

---

<div align="center">

**swpreq**

High-performance HTTP for Python.

Developed by **SilentWolfProject**

</div>
