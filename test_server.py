import json
import socketserver


API_FILES_RESPONSE_STATUS = [0]

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass


class MyRequestHandler(socketserver.StreamRequestHandler):
    """
    Request handler for testing metadisk.py.

    """
    data = None

    def handle(self):
        self.data = self.rfile.readline().strip().split()
        url = self.data[1].decode("utf-8").replace('/', '_')
        message = getattr(self, 'response{}'.format(url))()
        self.wfile.write(message)

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

    @staticmethod
    def response_api_audit_():
        pass
