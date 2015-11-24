import json
import socketserver

from urllib.parse import parse_qs
from hashlib import sha256

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
    body = {}
    path = None
    query_data = {}

    def handle(self):
        """
        Method to handle requests
        :return: None
        """
        self.data = self.request.recv(1024).strip()
        self.parse_request(self.data.decode("utf-8"))
        url = self.path.replace('/', '_')
        message = getattr(self, 'response_{}'.format(url))()
        self.request.sendall(message)

    def parse_request(self, req):
        """
        Method to parse request and set to class request attributes
            - self.path - url path "path/to/something"
            - self.method - http method type
            - self.headers - http headers
            - self.body - request body data
            - self.query_data - request query data
        :param req: request string
        """
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
            self.path, query_string = self.path.split("?")
            self.query_data = parse_qs(query_string)

    @staticmethod
    def _set_body(body, status_code=200,
                  is_json=True, file_name='TEST_FILE_NAME'):
        """
        Set body message for response
        :param body: dict or list
        :return: byte, response string
        """
        message = b'HTTP/1.0 ' + str.encode(str(status_code)) + b' OK\n'

        if is_json:
            body = str.encode(json.dumps(body)) + b'\n'
        else:
            body = body + b'\n'

        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(body),
        }
        if not is_json:
            headers['X-Sendfile'] = file_name
        for line in sorted(headers.items()):
            message += bytes('%s: %s\n' % line, 'utf-8')

        message += b'\n' + body
        return message

    def response_api_nodes_me_(self):
        """
        Preparing the response string for the "python metadisk.py info"
        command call.
        :return: byte, response string
        """
        json_prototype = {
          "public_key": "13LWbTkeuu4Pz7nFd6jCEEAwLfYZsDJSnK",
          "bandwidth": {
            "total": {
              "incoming": 0,
              "outgoing": 0
            },
            "current": {
              "incoming": 0,
              "outgoing": 0
            },
            "limits": {
              "incoming": None,
              "outgoing": None
            }
          },
          "storage": {
            "capacity": 524288000,
            "used": 0,
            "max_file_size": 0
          }
        }
        return self._set_body(json_prototype)

    def response_api_files_(self):
        """
        Generate an appropriate response string for the specific case
        of the "python metadisk.py files" and "python metadisk.py upload ..."
        command call.
        :return: byte, response string
        """
        if self.method == 'GET':
            choose = {
                1: self._set_body([]),
                2: self._set_body([1, 2])
            }
            API_FILES_RESPONSE_STATUS[0] += 1
            return choose[API_FILES_RESPONSE_STATUS[0]]
        else:
            boundary = self.headers['Content-Type'].split('boundary=')[-1]
            data = self.data.decode()
            part_of_body = data.split('\r\n--' + boundary)
            for item in part_of_body:
                if 'filename' in item:
                    file_data_part = item
            file_data = file_data_part.partition('\r\n\r\n')[-1]
            file_content = file_data.encode()
            data_hash = sha256(file_content).hexdigest()
            file_role = self.data.decode().split('"file_role"\r\n\r\n')[1][:3]
            message_content = {
                "data_hash": data_hash,
                "file_role": file_role
            }
            return self._set_body(message_content)

    def response_api_audit_(self):
        """
        Method to get audit data
        :return: bytes, response string
        """
        data_hash = '3a6eb0790f39ac87c94f3856b2dd2c5' \
                    'd110e6811602261a9a923d3bb23adc8b7'
        challenge_seed = '19b25856e1c150ca834cffc8b59b23ad' \
                         'bd0ec0389e58eb22b3b64768098d002b'
        if data_hash in self.body['data_hash'] \
                and challenge_seed in self.body['challenge_seed']:
            return self._set_body({
                "data_hash": "3a6eb0790f39ac87c94f3856b2dd2c5d"
                             "110e6811602261a9a923d3bb23adc8b7",
                "challenge_seed": "19b25856e1c150ca834cffc8b59b23ad"
                                  "bd0ec0389e58eb22b3b64768098d002b",
                "challenge_response": "a068cf9870a41ecc36e18be9277bc353"
                                      "f88e29ad8a1b2a778581b37453de7692"
            })
        return self._set_body({'error_code': 102})

    def response_api_files_test_not_valid_data_hash(self):
        """
        Method to get error when invalid data send
        """
        return self._set_body({'error_code': 101}, 400)

    def response_api_files_test_valid_data_hash(self):
        """
        Method to get data when valid data send
        """
        bin_data = b'TEST_DATA'
        if 'file_alias' in self.query_data:
            return self._set_body(bin_data, is_json=False,
                                  file_name=self.query_data['file_alias'][0])
        return self._set_body(bin_data, is_json=False)
