import json
import socketserver
from urllib.parse import urlparse, parse_qs


API_FILES_RESPONSE_STATUS = [0]

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MyRequestHandler(socketserver.BaseRequestHandler):
    """
    Request handler for testing metadisk.py.

    """
    data = None
    method = None
    headers = None
    body = None
    path = None
    query_string = None

    def handle(self):
        """
        Met
        :return:
        """
        self.data = self.request.recv(1024).strip()
        self.parse_request(self.data.decode("utf-8"))
        url = self.path.replace('/', '_')
        message = getattr(self, 'response_{}'.format(url))()
        self.request.sendall(message)

    def parse_request(self, req):
        headers = {}
        lines = req.splitlines()
        in_body = False
        body = ''
        for line in lines[1:]:
            if line.strip() == "":
                in_body = True
            if in_body:
                body += line
            else:
                k, v = line.split(":", 1)
                headers[k.strip()] = v.strip()
        method, path, _ = lines[0].split()
        self.path = path.lstrip("/")
        self.method = method
        self.headers = headers
        self.body = parse_qs(body)

        if '?' in path:
            self.path, self.query_string = self.path.split("?")
            self.query_string = parse_qs(self.query_string)


    @staticmethod
    def _set_body(body):
        message = b'HTTP/1.0 200 OK\n'
        body = str.encode(json.dumps(body)) + b'\n'
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(body),
        }
        for line in sorted(headers.items()):
            message += bytes('%s: %s\n' % line, 'utf-8')
        message += b'\n' + body
        return message

    def response_api_files_(self):

        choose = {
            1: self._set_body([]),
            2: self._set_body([1, 2])
        }
        API_FILES_RESPONSE_STATUS[0] += 1
        return choose[API_FILES_RESPONSE_STATUS[0]]

    def response_api_audit_(self):
        data_hash = '3a6eb0790f39ac87c94f3856b2dd2c5d110e6811602261a9a923d3bb23adc8b7'
        challenge_seed = '19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b'

        return self._set_body({'error_code': 102})
