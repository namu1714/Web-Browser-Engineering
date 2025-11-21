import socket
import ssl

class URL:
  # Cache persistent connections keyed by (scheme, host, port) -> socket
  _connections = {}

  def __init__(self, url):
    self.scheme, rest = url.split("://", 1)
    if self.scheme == "http":
      self.port = 80
    elif self.scheme == "https":
      self.port = 443

    # split host[:port] and path
    if "/" in rest:
      hostpart, pathpart = rest.split("/", 1)
      self.path = "/" + pathpart
    else:
      hostpart = rest
      self.path = "/"

    if ":" in hostpart:
      host, port = hostpart.split(":", 1)
      self.host = host
      self.port = int(port)
    else:
      self.host = hostpart

  def request(self):
    key = (self.scheme, self.host, self.port)

    s = URL._connections.get(key)
    if s is None:
      s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,
      )
      if self.scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=self.host)

      s.connect((self.host, self.port))
      URL._connections[key] = s

    # Send HTTP/1.1 with Connection: keep-alive to reuse the TCP connection.
    request = "GET {} HTTP/1.1\r\n".format(self.path)
    request += "Host: {}\r\n".format(self.host)
    request += "User-Agent: browser01-ex1.py\r\n"
    request += "Connection: keep-alive\r\n"
    request += "\r\n"
    s.send(request.encode("utf8"))

    # Read response headers first (until \r\n\r\n)
    buffer = b""
    while b"\r\n\r\n" not in buffer:
      data = s.recv(4096)
      if not data:
        # connection closed unexpectedly; remove from pool and raise
        try:
          del URL._connections[key]
        except KeyError:
          pass
        raise ConnectionError("connection closed while reading headers")
      buffer += data

    header_data, rest = buffer.split(b"\r\n\r\n", 1)
    header_lines = header_data.split(b"\r\n")
    statusline = header_lines[0].decode("utf8")
    version, status, explanation = statusline.split(" ", 2)
    print("Version:", version)
    print("Status:", status)
    print("Explanation:", explanation)

    response_headers = {}
    for line in header_lines[1:]:
      if not line:
        continue
      header, value = line.split(b":", 1)
      response_headers[header.decode("utf8").casefold()] = value.decode("utf8").strip()

    assert "transfer-encoding" not in response_headers
    assert "content-encoding" not in response_headers

    # If Content-Length is provided, read exactly that many bytes and keep socket open.
    if "content-length" in response_headers:
      length = int(response_headers["content-length"])
      body = rest
      remaining = length - len(body)
      while remaining > 0:
        chunk = s.recv(min(4096, remaining))
        if not chunk:
          # unexpected close
          try:
            del URL._connections[key]
          except KeyError:
            pass
          raise ConnectionError("connection closed while reading body")
        body += chunk
        remaining -= len(chunk)

      return body.decode("utf8", errors="replace")
    else:
      # No content-length: fall back to reading until close, and then close socket
      body = rest
      while True:
        chunk = s.recv(4096)
        if not chunk:
          break
        body += chunk

      # server closed connection; remove and close our socket
      try:
        s.close()
      except Exception:
        pass
      try:
        del URL._connections[key]
      except KeyError:
        pass

      return body.decode("utf8", errors="replace")

  @classmethod
  def close_all_connections(cls):
    for k, s in list(cls._connections.items()):
      try:
        s.close()
      except Exception:
        pass
    cls._connections.clear()

def show(body):
  in_tag = False
  for c in body:
    if c == "<":
      in_tag = True
    elif c == ">":
      in_tag = False
    elif not in_tag:
      print(c, end="")

def load(url):
  body = url.request()
  show(body)

if __name__ == "__main__":
  import sys
  load(URL(sys.argv[1]))
    