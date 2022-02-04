#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust, Lewis Ning
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
from urllib.parse import urlparse, urlencode


def help():
    print("httpclient.py [GET/POST] [URL]\n")


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    def get_host_port(self, url):
        parsed = urlparse(url)
        scheme = parsed.scheme
        port = parsed.port

        if port is None:
            if scheme == 'http':
                port = 80
            elif scheme == 'https':
                port = 443
        return int(port)

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = data.split()[1]
        return int(code)

    def get_headers(self, data):
        header = data.split('\r\n\r\n')[0]
        return header

    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body

    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))

    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        # Get each part of url
        parsed = urlparse(url)

        port = self.get_host_port(url)
        host = parsed.hostname
        path = parsed.path

        # Start the socket connection
        self.connect(host, port)

        # Send the HTTP Header to the server
        if path == '':
            message = f'GET / HTTP/1.1\r\nHost: {host}\r\nAccept-Language: en-US,en;q=0.5\r\n' \
                      f'Connection: close\r\n\r\n'
        else:
            message = f'GET {path} HTTP/1.1\r\nHost: {host}\r\nAccept-Language: en-US,en;q=0.5\r\n' \
                      f'Connection: close\r\n\r\n'

        self.sendall(message)
        received = self.recvall(self.socket)
        self.close()

        # Get code, header, body of the message received from server
        header = self.get_headers(received)
        code = self.get_code(header)
        body = self.get_body(received)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        # Get each part of url
        parsed = urlparse(url)

        port = self.get_host_port(url)
        host = parsed.hostname
        path = parsed.path

        # Start the socket connection
        self.connect(host, port)

        # Encoding the payload
        payload = None
        if args is not None:
            payload = urlencode(args)

        # Send the HTTP Header to the server
        if payload is not None:
            message = f'POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept-Language: en-US,en;q=0.5\r\n' \
                      f'Content-Length: {len(payload)}\r\nConnection: close\r\n\r\n{payload}\r\n\r\n'
        else:
            message = f'POST {path} HTTP/1.1\r\nHost: {host}\r\nAccept-Language: en-US,en;q=0.5\r\n' \
                      f'Content-Length: 0\r\nConnection: close\r\n\r\n'

        self.sendall(message)
        received = self.recvall(self.socket)
        self.close()

        # Get code, header, body of the message received from server
        header = self.get_headers(received)
        code = self.get_code(header)
        body = self.get_body(received)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if command == "POST":
            return self.POST(url, args)
        else:
            return self.GET(url, args)


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if len(sys.argv) <= 1:
        help()
        sys.exit(1)
    elif len(sys.argv) == 3:
        print(client.command(sys.argv[2], sys.argv[1]))
    else:
        print(client.command(sys.argv[1]))
