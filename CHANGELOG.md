# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- `Response.reason` property (HTTP reason phrase)
- `Response.elapsed` as `timedelta` for `requests` compatibility
- HTTP/3 (QUIC) support (experimental)
- Persistent cookie jar with disk save/load
- Session-level default params

## [0.2.0] - 2026-10-07

### Added
- Comprehensive test suite with 164 tests covering all public APIs (100% pass rate)
- Full async API coverage: `AsyncClient`, `AsyncSession`, `map()`, `gather()`
- WebSocket support via `AsyncWebSocket` with callback-based handlers
- Server-Sent Events (SSE) support via `client.sse()`
- `MultipartBuilder` with `.text()`, `.bytes()`, and `.file()` methods
- OAuth 1.0a helpers (`OAuth1`, `OAuth1Params`) and OAuth 2.0 (`OAuth2`)
- Retry policies: `RetryPolicy.default()`, `.none()`, `.aggressive()`, `.conservative()`, and custom
- Request and response hooks via `register_request_hook()` and `register_response_hook()`
- Adapter / mount support via `Client.mount()` and `Client.unmount()`
- Streaming helpers: `stream.iter_content()`, `stream.iter_lines()`, `stream.iter_json()`
- `SwpreqError` base class with 14 specialized exception types
- Platform detection functions: `get_platform_info()` and `detect_platform()`
- Content-Encoding support: gzip, brotli, zstd, deflate
- HTTP/2 support via `Client(http2=True)`
- Connection pool configuration via `Client(pool_size=N)`
- TLS verification toggle via `Client(verify=False)`
- `Client.get_json()` and `Client.post_json()` convenience helpers
- Proxy support: HTTP, HTTPS, SOCKS4, SOCKS5
- `.netrc` authentication lookup

### Changed
- Version bumped to 0.2.0 to match `swpreq-core` 0.2.0
- `pyproject.toml` metadata updated with full classifier list
- `README.md` rewritten with complete feature tables and API reference
- Exception classes re-exported from top-level `swpreq` namespace

### Fixed
- Version string consistency across `pyproject.toml`, `swpreq/__init__.py`, and native core
- `detect_platform()` now returns a tuple `(os, arch)` consistently across platforms
- Response header lookup now case-insensitive in examples and docs

### Performance
- Sequential benchmark: up to 8.98x faster than `requests`
- Async concurrent benchmark: 26.2 req/s with 50 concurrent requests
- Highest measured speedup: 21.10x for 200 concurrent requests vs `requests`
- HTTP/2 multiplexing reduces connection overhead on parallel workloads

### Documentation
- Added comprehensive README with feature matrix, API reference, and error table
- Added CHANGELOG following Keep a Changelog format
- Added compatibility matrix between `swpreq-py` and `swpreq-core`

### Compatibility
- Requires `swpreq-core` v0.2.0
- Python 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- Windows (x64, arm64, x86), Linux (x64, arm64, armv7), macOS (x64, arm64), Android (arm64, armv7, x64, x86)

## [0.1.0] - 2026-10-07

### Added
- Initial release
- Sync HTTP client: `Client`, `Session`
- Async HTTP client: `AsyncClient`, `AsyncSession`
- HTTP/1.1 and HTTP/2 support
- WebSocket support (Rust core)
- SSE support
- Streaming responses
- Multipart upload
- OAuth 1.0a and OAuth 2.0 helpers
- Retry policy with exponential backoff and jitter
- Request and response hooks
- Adapter (mount / unmount)
- Cookie jar
- `.netrc` support
- Encoding detection (BOM, charset)
- gzip, brotli, zstd, deflate compression
- Multi-platform support: Windows, Linux, macOS, Android
- Multi-arch support: x64, arm64, armv7, x86

### Performance
- 10.48x faster than `requests` (sequential, remote)
- 30.4 req/s async concurrent
- 3x to 21x speedup across workloads

[Unreleased]: https://github.com/silentwolfproject/swpreq-py/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/silentwolfproject/swpreq-py/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/silentwolfproject/swpreq-py/releases/tag/v0.1.0