<div align="center">

<img src="https://raw.githubusercontent.com/silentwolfproject/swpreq-py/main/assets/banner.png" alt="swpreq" width="100%" />

# swpreq

**High-performance HTTP client for Python with a Rust core.**

Up to **21.10x faster than `requests`** in the tested asynchronous concurrent workload.

[![PyPI](https://img.shields.io/pypi/v/swpreq.svg)](https://pypi.org/project/swpreq/)
[![Python](https://img.shields.io/pypi/pyversions/swpreq.svg)](https://pypi.org/project/swpreq/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS%20%7C%20Android-lightgrey.svg)](#platform-support)

[Installation](#installation) ·
[Quick Start](#quick-start) ·
[Features](#features) ·
[Examples](#examples) ·
[API Reference](#api-reference) ·
[Benchmark](#benchmark)

</div>

---

## About

`swpreq` is a Python HTTP client powered by a native Rust core.

It provides synchronous and asynchronous APIs for HTTP communication with support for:

* HTTP/1.1 and HTTP/2
* Native asynchronous execution
* WebSocket
* Server-Sent Events (SSE)
* Streaming responses
* Multipart uploads
* OAuth 1.0a and OAuth 2.0
* Cookies
* Proxies
* Redirect handling
* Retry policies
* Request and response hooks
* Compression
* TLS
* Connection pooling
* Custom client mounting
* Platform detection

The Python layer provides the developer-facing API while lower-level HTTP processing is handled by the native Rust core.

### Core Architecture

| Component             | Implementation               |
| :-------------------- | :--------------------------- |
| HTTP implementation   | Native Rust                  |
| Python interface      | C ABI + `ctypes`             |
| API model             | Synchronous and asynchronous |
| HTTP protocols        | HTTP/1.1 and HTTP/2          |
| Connection management | Rust core                    |
| TLS                   | Rustls with TLS 1.3          |
| Concurrency           | Native async execution       |
| Distribution          | Prebuilt native binaries     |

---

# Installation

Install the latest version from PyPI:

```bash
pip install swpreq
```

Prebuilt native binaries are included for supported targets, so a Rust toolchain is not required for normal installation.

### Requirements

| Requirement       | Version                        |
| :---------------- | :----------------------------- |
| Python            | 3.8+                           |
| Operating systems | Windows, Linux, macOS, Android |
| Architectures     | x64, arm64, armv7, x86         |

---

# Quick Start

## Basic Request

The simplest way to send an HTTP request is through the module-level API:

```python
import swpreq

response = swpreq.get("https://httpbin.org/get")

print(response.status_code)
print(response.json())
```

Every request returns a `Response` object containing status information, headers, body data, URL information, timing data, and related metadata.

## Query Parameters and Headers

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

## JSON Requests

Use `json` for JSON request bodies:

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

Use `Client` when multiple requests share configuration such as headers, cookies, retries, or connection state.

```python
from swpreq import Client

with Client() as client:
    client.set_header("Authorization", "Bearer token")

    response = client.get(
        "https://httpbin.org/headers"
    )

    print(response.status_code)
```

## Asynchronous Requests

Use `AsyncClient` for asynchronous workloads:

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

## Concurrent Requests

For multiple independent requests, `AsyncClient.map()` can execute requests concurrently:

```python
import asyncio
from swpreq import AsyncClient

async def main():
    urls = [
        f"https://httpbin.org/get?i={i}"
        for i in range(100)
    ]

    async with AsyncClient(max_workers=32) as client:
        responses = await client.map(urls)

    successful = sum(
        1 for response in responses
        if response.is_success
    )

    print(f"{successful}/100 succeeded")

asyncio.run(main())
```

---

# Features

| Feature     | Description                                              |
| :---------- | :------------------------------------------------------- |
| HTTP/1.1    | Keep-alive and chunked transfer support                  |
| HTTP/2      | Multiplexing and header compression                      |
| Sync API    | `Client`, `Session`, and module-level requests           |
| Async API   | `AsyncClient`, `AsyncSession`, `map`, and `gather`       |
| WebSocket   | Full-duplex communication through `AsyncWebSocket`       |
| SSE         | Server-Sent Events through `client.sse()`                |
| Streaming   | Content, line, and JSON iterators                        |
| Multipart   | Text, bytes, and file uploads                            |
| OAuth       | OAuth 1.0a and OAuth 2.0 helpers                         |
| Retry       | Configurable retries with exponential backoff and jitter |
| Hooks       | Request and response hooks                               |
| Cookies     | Cookie storage and per-domain handling                   |
| Proxy       | HTTP, HTTPS, SOCKS4, and SOCKS5                          |
| Redirects   | Configurable redirect behavior and limits                |
| Timeout     | Per-request and per-client configuration                 |
| Compression | gzip, brotli, zstd, and deflate                          |
| TLS         | Rustls with TLS 1.3                                      |
| Netrc       | `.netrc` authentication lookup                           |
| Adapter     | Mount custom clients to URL prefixes                     |
| Platform    | Windows, Linux, macOS, and Android                       |

---

# HTTP Methods

All standard HTTP methods are available through the module-level API, `Client`, and `AsyncClient`.

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

swpreq.delete("https://httpbin.org/delete")

swpreq.head("https://httpbin.org/get")

swpreq.options("https://httpbin.org/get")

swpreq.request(
    "GET",
    "https://httpbin.org/get",
)
```

### Available Methods

| Function    | Description        |
| :---------- | :----------------- |
| `get()`     | HTTP GET           |
| `post()`    | HTTP POST          |
| `put()`     | HTTP PUT           |
| `patch()`   | HTTP PATCH         |
| `delete()`  | HTTP DELETE        |
| `head()`    | HTTP HEAD          |
| `options()` | HTTP OPTIONS       |
| `request()` | Custom HTTP method |

---

# Response

Every request returns a `Response` object.

```python
import swpreq

response = swpreq.get("https://httpbin.org/json")

print(response.status_code)
print(response.text)
print(response.json())
```

## Response Properties

| Property           | Type    | Description                      |
| :----------------- | :------ | :------------------------------- |
| `status_code`      | `int`   | HTTP status code                 |
| `ok`               | `bool`  | Whether the status is below 400  |
| `is_success`       | `bool`  | Whether the response is 2xx      |
| `is_redirect`      | `bool`  | Whether the response is 3xx      |
| `is_client_error`  | `bool`  | Whether the response is 4xx      |
| `is_server_error`  | `bool`  | Whether the response is 5xx      |
| `headers`          | `dict`  | Response headers                 |
| `cookies`          | `dict`  | Response cookies                 |
| `links`            | `dict`  | Parsed link headers              |
| `content`          | `bytes` | Raw response body                |
| `text`             | `str`   | Decoded response body            |
| `encoding`         | `str`   | Response encoding                |
| `url`              | `str`   | Final URL after redirects        |
| `http_version`     | `str`   | HTTP version                     |
| `http_version_num` | `int`   | Numeric HTTP version             |
| `elapsed_ms`       | `int`   | Request duration in milliseconds |
| `history`          | `list`  | Redirect history                 |
| `request_id`       | `str`   | Server-provided request ID       |

## Response Methods

| Method               | Returns       | Description                          |
| :------------------- | :------------ | :----------------------------------- |
| `json()`             | `Any`         | Parse response body as JSON          |
| `header(name)`       | `str \| None` | Read a response header               |
| `cookie(name)`       | `str \| None` | Read a response cookie               |
| `link(rel)`          | `str \| None` | Read a link by relation              |
| `next_page_url()`    | `str \| None` | Get the next URL from a Link header  |
| `iter_content(n)`    | `Iterator`    | Iterate over byte chunks             |
| `iter_lines()`       | `Iterator`    | Iterate over response lines          |
| `iter_json()`        | `Iterator`    | Iterate over JSON objects            |
| `raise_for_status()` | `None`        | Raise an error for 4xx/5xx responses |

---

# Client and Session

`Client` and `Session` allow configuration to be reused across multiple requests.

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

## Client Methods

| Method                     | Parameters                                                                      | Description                    |
| :------------------------- | :------------------------------------------------------------------------------ | :----------------------------- |
| `Client()`                 | `timeout`, `user_agent`, `verify`, `http2`, `pool_size`, `retry`, `max_workers` | Create a reusable client       |
| `get()`                    | `url, **kwargs`                                                                 | GET request                    |
| `post()`                   | `url, **kwargs`                                                                 | POST request                   |
| `put()`                    | `url, **kwargs`                                                                 | PUT request                    |
| `patch()`                  | `url, **kwargs`                                                                 | PATCH request                  |
| `delete()`                 | `url, **kwargs`                                                                 | DELETE request                 |
| `head()`                   | `url, **kwargs`                                                                 | HEAD request                   |
| `options()`                | `url, **kwargs`                                                                 | OPTIONS request                |
| `request()`                | `method, url, **kwargs`                                                         | Custom HTTP request            |
| `get_json()`               | `url, **kwargs`                                                                 | GET and parse JSON             |
| `post_json()`              | `url, json, **kwargs`                                                           | POST JSON and parse response   |
| `set_header()`             | `name, value`                                                                   | Set default header             |
| `update_headers()`         | `dict`                                                                          | Update default headers         |
| `remove_header()`          | `name`                                                                          | Remove a default header        |
| `clear_headers()`          | —                                                                               | Remove all default headers     |
| `set_cookie()`             | `name, value, domain`                                                           | Set a cookie                   |
| `clear_cookies()`          | —                                                                               | Clear all cookies              |
| `set_retry()`              | `RetryPolicy`                                                                   | Set retry policy               |
| `mount()`                  | `prefix, client`                                                                | Mount a client to a URL prefix |
| `unmount()`                | `prefix`                                                                        | Remove a mounted client        |
| `register_request_hook()`  | `callable`                                                                      | Register request hook          |
| `register_response_hook()` | `callable`                                                                      | Register response hook         |
| `stream()`                 | `method, url, **kwargs`                                                         | Create a streaming request     |
| `sse()`                    | `url, **kwargs`                                                                 | Create an SSE stream           |
| `multipart()`              | —                                                                               | Create a `MultipartBuilder`    |
| `close()`                  | —                                                                               | Close the client               |

## Client Configuration

| Parameter     | Type          | Default | Description                |
| :------------ | :------------ | :------ | :------------------------- |
| `timeout`     | `float`       | `30.0`  | Default request timeout    |
| `user_agent`  | `str`         | —       | Default User-Agent         |
| `verify`      | `bool`        | `True`  | Verify TLS certificates    |
| `http2`       | `bool`        | `False` | Enable HTTP/2              |
| `pool_size`   | `int`         | —       | Connection pool size       |
| `retry`       | `RetryPolicy` | —       | Retry configuration        |
| `max_workers` | `int`         | —       | Maximum concurrent workers |

---

# Asynchronous API

`AsyncClient` provides asynchronous request handling and concurrent execution.

Its request methods mirror the synchronous `Client` API.

## Concurrent Mapping

```python
import asyncio
from swpreq import AsyncClient

async def main():
    urls = [
        f"https://httpbin.org/get?i={i}"
        for i in range(100)
    ]

    async with AsyncClient(max_workers=32) as client:
        responses = await client.map(urls)

    successful = [
        response
        for response in responses
        if response.is_success
    ]

    print(f"{len(successful)}/100 succeeded")

asyncio.run(main())
```

## Gathering Requests

```python
import asyncio
from swpreq import AsyncClient

async def main():
    async with AsyncClient() as client:
        r1, r2, r3 = await client.gather(
            client.get("https://httpbin.org/get?x=1"),
            client.get("https://httpbin.org/get?x=2"),
            client.get("https://httpbin.org/get?x=3"),
        )

        print(r1.json()["args"]["x"])
        print(r2.json()["args"]["x"])
        print(r3.json()["args"]["x"])

asyncio.run(main())
```

## AsyncClient Methods

| Method              | Returns          | Description               |
| :------------------ | :--------------- | :------------------------ |
| `await c.get()`     | `Response`       | Async GET                 |
| `await c.post()`    | `Response`       | Async POST                |
| `await c.put()`     | `Response`       | Async PUT                 |
| `await c.patch()`   | `Response`       | Async PATCH               |
| `await c.delete()`  | `Response`       | Async DELETE              |
| `await c.head()`    | `Response`       | Async HEAD                |
| `await c.options()` | `Response`       | Async OPTIONS             |
| `await c.request()` | `Response`       | Async custom request      |
| `await c.map()`     | `list[Response]` | Send URLs concurrently    |
| `await c.gather()`  | `list[Response]` | Await multiple coroutines |
| `await c.close()`   | `None`           | Close the client          |

---

# Request Parameters

Request methods support common HTTP configuration through keyword arguments.

| Parameter         | Type                   | Default | Description                          |
| :---------------- | :--------------------- | :------ | :----------------------------------- |
| `params`          | `dict`                 | `None`  | Query parameters                     |
| `headers`         | `dict`                 | `None`  | Request headers                      |
| `data`            | `dict \| str \| bytes` | `None`  | Form or raw request data             |
| `json`            | `Any`                  | `None`  | JSON request body                    |
| `body`            | `bytes`                | `None`  | Raw request body                     |
| `files`           | `MultipartBuilder`     | `None`  | Multipart upload                     |
| `timeout`         | `float`                | `30.0`  | Request timeout in seconds           |
| `proxy`           | `str`                  | `None`  | HTTP, HTTPS, SOCKS4, or SOCKS5 proxy |
| `allow_redirects` | `bool`                 | `True`  | Follow redirects                     |
| `max_redirects`   | `int`                  | `10`    | Maximum redirect count               |
| `stream`          | `bool`                 | `False` | Enable streaming                     |

---

# Timeouts

Timeouts can be configured per request or through a client.

```python
import swpreq

response = swpreq.get(
    "https://httpbin.org/delay/1",
    timeout=30.0,
)
```

Timeouts can be handled explicitly:

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

Retries are configured through `RetryPolicy`.

```python
from swpreq import Client, RetryPolicy

with Client(
    retry=RetryPolicy.aggressive()
) as client:
    response = client.get(
        "https://httpbin.org/get"
    )
```

## Presets

| Policy                       | Description                       |
| :--------------------------- | :-------------------------------- |
| `RetryPolicy()`              | Default policy with 3 retries     |
| `RetryPolicy.none()`         | Disable retries                   |
| `RetryPolicy.aggressive()`   | 5 retries with aggressive backoff |
| `RetryPolicy.conservative()` | 2 retries with gentle backoff     |

## Parameters

| Parameter       | Type   | Default | Description                |
| :-------------- | :----- | :------ | :------------------------- |
| `max_retries`   | `int`  | `3`     | Maximum retry attempts     |
| `base_delay_ms` | `int`  | —       | Base retry delay           |
| `exponential`   | `bool` | `True`  | Enable exponential backoff |
| `jitter`        | `bool` | —       | Add randomized delay       |

---

# Redirects

Redirect handling can be configured per request.

### Follow Redirects

```python
import swpreq

response = swpreq.get(
    "https://httpbin.org/redirect/3"
)
```

### Disable Redirects

```python
response = swpreq.get(
    "https://httpbin.org/redirect/1",
    allow_redirects=False,
)
```

### Limit Redirects

```python
response = swpreq.get(
    "https://httpbin.org/redirect/10",
    max_redirects=3,
)
```

---

# Streaming

Streaming allows response data to be processed incrementally instead of loading the entire response into memory.

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

## Streaming Methods

| Method            | Returns    | Description                 |
| :---------------- | :--------- | :-------------------------- |
| `iter_content(n)` | `Iterator` | Iterate over byte chunks    |
| `iter_lines()`    | `Iterator` | Iterate over response lines |
| `iter_json()`     | `Iterator` | Iterate over JSON objects   |

---

# Multipart

`MultipartBuilder` supports text fields, binary data, and files.

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

## MultipartBuilder

| Method    | Parameters                           | Description                |
| :-------- | :----------------------------------- | :------------------------- |
| `text()`  | `name, value`                        | Add a text field           |
| `bytes()` | `name, data, filename, content_type` | Add binary data            |
| `file()`  | `name, path`                         | Add a file from disk       |
| `len()`   | —                                    | Return the number of parts |

---

# Authentication

## OAuth 1.0a

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

### OAuth1Params

| Field             | Type  | Description                  |
| :---------------- | :---- | :--------------------------- |
| `consumer_key`    | `str` | OAuth consumer key           |
| `consumer_secret` | `str` | OAuth consumer secret        |
| `token`           | `str` | Optional access token        |
| `token_secret`    | `str` | Optional access token secret |

### OAuth1 Methods

| Method                     | Returns | Description                                 |
| :------------------------- | :------ | :------------------------------------------ |
| `OAuth1.generate_header()` | `str`   | Generate an OAuth 1.0a authorization header |

## OAuth 2.0

### Bearer Authentication

```python
from swpreq import OAuth2

headers = OAuth2.bearer_header(
    "my-token"
)
```

### Client Credentials

```python
from swpreq import OAuth2

token = OAuth2.client_credentials(
    token_url="https://api.example.com/oauth/token",
    client_id="client-id",
    client_secret="client-secret",
    scope="read write",
)
```

### OAuth2 Methods

| Method                        | Returns | Description                            |
| :---------------------------- | :------ | :------------------------------------- |
| `OAuth2.bearer_header()`      | `dict`  | Build a Bearer authorization header    |
| `OAuth2.client_credentials()` | `str`   | Fetch a token using client credentials |

---

# Cookies

Cookies can be configured through a reusable client.

```python
from swpreq import Client

with Client() as client:
    client.set_cookie(
        "session",
        "xyz789",
        ".example.com",
    )

    response = client.get(
        "https://example.com/account"
    )
```

Available client operations:

```text
set_cookie(name, value, domain)
clear_cookies()
```

Cookie storage supports per-domain handling.

---

# Hooks

Request and response hooks allow application-specific processing around requests.

```python
from swpreq import Client

with Client() as client:

    def request_hook(request):
        request["headers"]["X-Hook"] = "yes"
        return request

    def response_hook(response):
        print(
            f"Received {response.status_code} "
            f"from {response.url}"
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

| Method                     | Parameters | Description                       |
| :------------------------- | :--------- | :-------------------------------- |
| `register_request_hook()`  | `callable` | Called before sending a request   |
| `register_response_hook()` | `callable` | Called after receiving a response |

---

# WebSocket

WebSocket communication is available through `AsyncWebSocket`.

## Context Manager

```python
import asyncio
from swpreq import AsyncWebSocket

async def main():
    async with AsyncWebSocket(
        "wss://echo.websocket.events"
    ) as websocket:

        await websocket.send_text("Hello")

        message = await websocket.recv(
            timeout=5.0
        )

        print(message.data)

asyncio.run(main())
```

## Callback-Based Handling

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
        lambda message:
        print(f"received: {message.data}")
    )

    websocket.on_close(
        lambda code, reason:
        print(f"closed: {code}")
    )

    websocket.on_error(
        lambda error:
        print(f"error: {error}")
    )

    await websocket.connect()

    await websocket.send_text("Hello")
    await websocket.send_json(
        {"hello": "world"}
    )
    await websocket.send_binary(
        b"binary data"
    )

    await asyncio.sleep(2)
    await websocket.close()

asyncio.run(main())
```

## AsyncWebSocket API

| Method          | Parameters | Description               |
| :-------------- | :--------- | :------------------------ |
| `connect()`     | —          | Open WebSocket connection |
| `close()`       | —          | Close connection          |
| `send_text()`   | `str`      | Send text frame           |
| `send_json()`   | `dict`     | Send JSON frame           |
| `send_binary()` | `bytes`    | Send binary frame         |
| `recv()`        | `timeout`  | Receive the next message  |
| `on_open()`     | `callable` | Register open callback    |
| `on_message()`  | `callable` | Register message callback |
| `on_close()`    | `callable` | Register close callback   |
| `on_error()`    | `callable` | Register error callback   |

---

# Server-Sent Events

SSE is available through the client's streaming interface.

```python
from swpreq import Client

with Client() as client:
    stream = client.sse(
        "https://example.com/events"
    )

    for event in stream:
        print(event)
```

## SSE Types

| Type        | Description                                    |
| :---------- | :--------------------------------------------- |
| `SseStream` | Iterable stream of SSE events                  |
| `SseEvent`  | Individual event containing data, ID, and type |

---

# Proxy Support

`swpreq` supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies.

```python
import swpreq

response = swpreq.get(
    "https://httpbin.org/ip",
    proxy="http://127.0.0.1:8080",
)

print(response.json())
```

The proxy can also be supplied as part of a reusable client configuration.

---

# Compression

The native core supports the following compression formats:

* gzip
* brotli
* zstd
* deflate

Compression handling is performed by the native layer.

---

# TLS

TLS is implemented through Rustls with TLS 1.3 support.

Certificate verification is enabled by default:

```python
from swpreq import Client

with Client(verify=True) as client:
    response = client.get(
        "https://example.com"
    )
```

---

# Netrc

`swpreq` supports `.netrc` authentication lookup.

This allows compatible credentials to be resolved from the user's `.netrc` configuration instead of being manually embedded into request code.

---

# Client Mounting

A custom client can be mounted to a URL prefix.

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

Mounted clients can be removed with:

```python
main.unmount(
    "https://api.example.com/"
)
```

---

# Error Handling

All library-specific exceptions inherit from `SwpreqError`.

| Exception                   | Code      | Description                        |
| :-------------------------- | :-------- | :--------------------------------- |
| `SwpreqError`               | —         | Base exception                     |
| `NetworkError`              | `1`       | Network-level error                |
| `TimeoutError`              | `2`       | Request timeout                    |
| `InvalidUrlError`           | `3`       | Invalid URL                        |
| `TlsError`                  | `4`       | TLS handshake failure              |
| `ProxyError`                | `5`       | Proxy connection failure           |
| `DecodeError`               | `6`       | Response decoding failure          |
| `EncodeError`               | `7`       | Request encoding failure           |
| `IOError`                   | `8`       | I/O failure                        |
| `InvalidArgumentError`      | `9`       | Invalid argument                   |
| `NotFoundError`             | `10`      | Resource not found                 |
| `HTTPError`                 | `4xx/5xx` | HTTP status error                  |
| `PlatformNotSupportedError` | —         | Unsupported platform               |
| `CoreLoadError`             | —         | Native library could not be loaded |
| `FileLockedError`           | —         | Native library is locked           |

### Example

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
    print(f"swpreq error: {error}")
```

---

# Examples

## Basic API Client

```python
import swpreq

response = swpreq.get(
    "https://api.example.com/users",
    headers={
        "Authorization": "Bearer TOKEN"
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

        responses = await client.map(urls)

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

## Download a Large Response

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

## Upload a File

```python
from swpreq import Client, MultipartBuilder

with Client() as client:
    multipart = (
        MultipartBuilder()
        .text(
            "description",
            "Example document",
        )
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

## Mount a Specialized Client

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

## Handle HTTP and Network Errors

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

## Detect the Current Platform

```python
import swpreq

info = swpreq.get_platform_info()

print("OS:", info["os"])
print("Architecture:", info["arch"])
print("Supported:", info["supported"])
print("Library:", info["library_name"])

os_name, arch = swpreq.detect_platform()

print(
    "Detected:",
    os_name,
    arch,
)
```

---

# API Reference

## Module-Level Functions

| Function           | Parameters              | Returns    | Description         |
| :----------------- | :---------------------- | :--------- | :------------------ |
| `swpreq.get()`     | `url, **kwargs`         | `Response` | HTTP GET            |
| `swpreq.post()`    | `url, **kwargs`         | `Response` | HTTP POST           |
| `swpreq.put()`     | `url, **kwargs`         | `Response` | HTTP PUT            |
| `swpreq.patch()`   | `url, **kwargs`         | `Response` | HTTP PATCH          |
| `swpreq.delete()`  | `url, **kwargs`         | `Response` | HTTP DELETE         |
| `swpreq.head()`    | `url, **kwargs`         | `Response` | HTTP HEAD           |
| `swpreq.options()` | `url, **kwargs`         | `Response` | HTTP OPTIONS        |
| `swpreq.request()` | `method, url, **kwargs` | `Response` | Custom HTTP request |

## Platform Functions

| Function                     | Returns | Description                                               |
| :--------------------------- | :------ | :-------------------------------------------------------- |
| `swpreq.get_lib()`           | `Any`   | Load and return the native library handle                 |
| `swpreq.get_platform_info()` | `dict`  | Return OS, architecture, support status, and library name |
| `swpreq.detect_platform()`   | `tuple` | Return `(os, arch)`                                       |

---

# Platform Support

| Platform | Architectures          | Status    |
| :------- | :--------------------- | :-------- |
| Windows  | x64, arm64, x86        | Supported |
| Linux    | x64, arm64, armv7      | Supported |
| macOS    | x64, arm64             | Supported |
| Android  | arm64, armv7, x64, x86 | Supported |

Prebuilt native binaries are included for supported targets. Normal installation does not require a local Rust build environment.

---

# Benchmark

Benchmark results below come from direct tests against the listed targets and environments.

They should be interpreted as results for the tested workloads, not as a universal performance guarantee for every network, server, payload, or hardware configuration.

## Test Environment

| Item           | Value         |
| :------------- | :------------ |
| OS             | Windows 11    |
| Python         | 3.10          |
| Remote target  | `httpbin.org` |
| Remote latency | ~500 ms       |
| Local target   | `localhost`   |

## swpreq vs requests

| Scenario                           | requests | swpreq |   Speedup  |
| :--------------------------------- | :------: | :----: | :--------: |
| Sequential remote, 50 requests     |  53.61s  | 14.33s |  **3.74x** |
| Sequential localhost, 500 requests |   4.85s  |  3.43s |  **1.41x** |
| Async concurrent, 50 requests      |  14.31s  |  2.12s |  **6.75x** |
| Async concurrent, 100 requests     |  29.60s  |  2.00s | **14.79x** |
| Async concurrent, 200 requests     |  61.98s  |  2.94s | **21.10x** |

The largest tested difference was **21.10x** on the 200-request asynchronous concurrent workload.

## swpreq vs aiohttp

| Scenario                      | aiohttp | swpreq |  Speedup  |
| :---------------------------- | :-----: | :----: | :-------: |
| Remote, 50 requests           |  1.74s  |  1.68s | **1.04x** |
| Remote, 100 requests          |  2.10s  |  2.00s | **1.05x** |
| Remote, 200 requests          |  2.62s  |  3.04s | **0.86x** |
| Remote JSON API, 100 requests |  0.64s  |  0.30s | **2.17x** |
| Worker = 128                  |  1.83s  |  1.46s | **1.26x** |
| Localhost, 500 requests       |  8.20s  |  4.50s | **1.82x** |

The results show that performance depends on the workload. `swpreq` was faster in most tested scenarios, but it was not faster in every test.

## Implementation Differences

| Layer               | requests           | swpreq                         |
| :------------------ | :----------------- | :----------------------------- |
| HTTP client         | urllib3            | reqwest                        |
| TLS                 | OpenSSL via Python | rustls                         |
| JSON processing     | Python             | Rust                           |
| Compression         | Python             | Rust                           |
| Connection handling | Python layer       | Rust core                      |
| Concurrency         | Blocking / manual  | Native async                   |
| GIL involvement     | Python execution   | Core processing outside Python |

---

# Architecture

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

The Python layer provides the public developer API while the native Rust core performs lower-level HTTP processing.

---

# Design Goals

`swpreq` is designed around several core goals:

* Keep the Python API straightforward.
* Move performance-sensitive HTTP processing into native code.
* Provide both synchronous and asynchronous interfaces.
* Support high-concurrency workloads.
* Provide reusable clients and connection state.
* Keep advanced HTTP functionality available without requiring separate libraries.
* Distribute prebuilt native binaries for supported platforms.

---

# Contributing

Contributions are welcome through the project repository.

The native Rust core is currently private. Contributions to the public Python layer and documentation are welcome.

---

# Related Projects

| Project       | Description      |
| :------------ | :--------------- |
| `swpreq-core` | Native Rust core |
| `swpreq-py`   | Python interface |

---

# License

MIT License.

See [`LICENSE`](LICENSE) for the complete license text.

---

<div align="center">

**swpreq**

High-performance HTTP for Python.

Developed by **SilentWolfProject**

</div>
