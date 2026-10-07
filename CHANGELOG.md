# Changelog

## [0.1.0] - 2026-10-07

### Added

- Initial release
- Sync HTTP client (Client, Session)
- Async HTTP client (AsyncClient, AsyncSession)
- HTTP/1.1 and HTTP/2 support
- WebSocket support (embedded in Rust)
- SSE support
- Streaming response
- Multipart upload
- OAuth1 and OAuth2 helpers
- Retry policy (exponential, jitter)
- Hooks (request, response)
- Adapter (mount, unmount)
- Cookie jar
- Netrc support
- Encoding detection (BOM, charset)
- gzip, brotli, zstd, deflate compression
- Multi-platform support (Windows, Linux, macOS, Android)
- Multi-arch support (x64, arm64, armv7, x86)

### Performance

- 10.48x faster than requests (sequential, remote)
- 30.4 req/s async concurrent
- 3-21x speedup across workloads