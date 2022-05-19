import re
import socket
import ssl

def request(url):

    headers = {}
    body=""

    scheme, url = url.split("://",1)
    assert scheme in ["http", "https", "file"]
    
    host, path = url.split("/",1)
    
    if scheme == "file":
        path = path.replace("%20"," ")
        with open(path, encoding="utf8") as f:
            body=f.read()
        return headers, body

    path ="/"+path


    if ":"in host:
        host, port = host.split(":",1)
        port = int(port)
    else:
        port = 80 if scheme == "http" else 443
    

    s= socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP
    )
    
    
    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)

    s.connect((host,port))

    req = RequestObj(path, "HTTP/1.1").add("Host", host).add("Connection", "close").add("User-Agent","None").wrap()
    print(req)
    s.send(req)

    response = s.makefile("r", encoding="utf8", newline="\r\n")

    statusline = response.readline()
    version, status, explanation = statusline.split(" ",2)
    assert status == "200", "{} : {}".format(status, explanation)

    
    while True:
        line = response.readline()
        if line == "\r\n":
            break
        header, value = line.split(":",1)
        headers[header.lower()] = value.strip()
    
    assert "transfer-encoding" not in headers
    assert "content-encoding" not in headers

    body = response.read()
    s.close()

    return headers, body

class RequestObj: 
    def __init__(self, path, httpversion="HTTP/1.0") -> None:
        self.request = "GET {} {}\r\n".format(path, httpversion).encode("utf8")
    
    def add(self,header, value, close=False):
        self.request += ("{}: {}\r\n".format(header, value).encode("utf8"))
        return self

    def wrap(self):
        return self.request + "\r\n".encode("utf8")


def show(body):
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")

def load(url="file:///D:/System/Pictures/Google.html"):
    headers, body = request(url)
    show(body)

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        load(sys.argv[1])
    else:
        load()

    


