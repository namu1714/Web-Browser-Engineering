# Web Browser Engineering Project

## Project Overview

This is an educational implementation of a web browser built from scratch, following a learning-by-building approach. The codebase demonstrates fundamental browser concepts through incremental implementations.

## Architecture & Design Philosophy

### Minimalist HTTP Client

- **Direct socket programming**: Uses Python's `socket` module directly rather than high-level HTTP libraries (like `requests`)
- **Educational intent**: Code prioritizes clarity and learning over production features
- **Incremental complexity**: Files named `browser01.py`, `browser02.py`, etc. represent progressive feature additions

### HTTP Protocol Implementation

The `URL` class handles both URL parsing and HTTP requests:

```python
# URL parsing extracts scheme, host, and path
url = URL("http://example.org/index.html")
url.scheme  # "http"
url.host    # "example.org"
url.path    # "/index.html"
```

**Critical design decisions:**

- Only HTTP is supported (no HTTPS) - assertion validates `self.scheme == "http"`
- HTTP/1.1 protocol with minimal headers (GET + Host only)
- Response parsing assumes simple encoding (no `transfer-encoding`, no `content-encoding`)

## Code Conventions

### Indentation & Style

- **2-space indentation** throughout (not PEP 8's standard 4 spaces)
- Maintains consistency with the educational material's formatting

### Error Handling

- Uses **assertions for protocol constraints** rather than exceptions
  ```python
  assert "transfer-encoding" not in response_headers
  assert "content-encoding" not in response_headers
  ```
- This reflects the educational nature - demonstrating what's NOT supported rather than handling all cases

### HTTP Protocol Details

- **CRLF line endings**: Uses `\r\n` for HTTP compliance
- **Case-insensitive headers**: `header.casefold()` normalizes header names
- **Socket cleanup**: Always closes sockets after reading response

## Development Workflow

### Running the Browser

```bash
python browser01.py
# Note: Currently only defines classes, no main execution block
```

### Testing

Since this is educational code without a test suite, test manually:

```python
from browser01 import URL
body = URL("http://example.org").request()
print(body)
```

## Key Implementation Patterns

### Socket Connection Setup

Always use this pattern for HTTP connections:

```python
s = socket.socket(
  family=socket.AF_INET,
  type=socket.SOCK_STREAM,
  proto=socket.IPPROTO_TCP,
)
s.connect((self.host, 80))
```

### Response Parsing Order

1. Read status line first
2. Parse headers until blank line (`\r\n`)
3. Store headers in dict with normalized keys
4. Read remaining content as body

## What This Code Does NOT Support

- HTTPS/TLS encryption
- HTTP methods other than GET
- Request headers beyond Host
- Transfer-encoding (chunked responses)
- Content-encoding (compressed responses)
- Redirects, cookies, or authentication
- Non-80 ports or custom port specifications

When extending this code, maintain these limitations for each numbered version, adding features incrementally in subsequent files.
