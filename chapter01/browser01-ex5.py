import socket
import ssl

class URL:
  def __init__(self, url):
    # Support view-source: scheme which wraps another URL like:
    #   view-source:http://example.org/
    self.view_source = False
    if url.startswith("view-source:"):
      self.view_source = True
      url = url[len("view-source:"):]
    
    self.scheme, url = url.split("://", 1)
    if self.scheme == "http":
      self.port = 80
    elif self.scheme == "https":
      self.port = 443

    if "/" not in url:
      url = url + "/"
    self.host, url = url.split("/", 1)
    self.path = "/" + url

    if ":" in self.host:
      self.host, port = self.host.split(":", 1)
      self.port = int(port)
  
  def request(self):
    # Supported HTTP/1.1
    s = socket.socket(
      family=socket.AF_INET,
      type=socket.SOCK_STREAM,
      proto=socket.IPPROTO_TCP,
    )
    if self.scheme == "https":
      ctx = ssl.create_default_context()
      s = ctx.wrap_socket(s, server_hostname=self.host)

    s.connect((self.host, self.port))

    request = "GET {} HTTP/1.1\r\n".format(self.path)
    request += "Host: {}\r\n".format(self.host)
    request += "Connection: close\r\n" # Ensure the server closes the connection
    request += "User-Agent: browser01-ex1.py\r\n"
    request += "\r\n"
    s.send(request.encode("utf8"))

    response = s.makefile("r", encoding="utf8", newline="\r\n")
    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)

    response_headers = {}
    while True:
      line = response.readline()
      if line == "\r\n": break
      header, value = line.split(":", 1)
      response_headers[header.casefold()] = value.strip()

    assert "transfer-encoding" not in response_headers
    assert "content-encoding" not in response_headers

    body = response.read()
    s.close()

    return body

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
  # If the URL was a view-source: wrapper, print raw source instead of stripping tags
  if getattr(url, "view_source", False):
    print(body)
  else:
    show(body)

if __name__ == "__main__":
  import sys
  load(URL(sys.argv[1]))
