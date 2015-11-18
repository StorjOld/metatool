import os
import sys
import json
import unittest
import time
import socketserver
import _thread

from hashlib import sha256


class MyRequestHandler(socketserver.StreamRequestHandler):
    """
    Request handler for testing metadisk.py.

    """

    def handle(self):
        """
        Temporary method, which response to "python metadisk.py files"
        command.
        :return: response with display of empty list
        """
        self.data = self.rfile.readline().strip()
        print("{} wrote:".format(self.client_address[0]))
        print(self.data)
        start_line = b'HTTP/1.0 200 OK\n'
        message = b'\n[]\n'
        headers = {
            'Content-Type': 'application/json',
            'Content-Length': len(message),
        }
        self.wfile.write(start_line)
        for line in sorted(headers.items()):
            self.wfile.write(bytes('%s: %s\n' % line, 'utf-8'))
        self.wfile.write(message)

    def finish(self):
        # You may run server like threading object and call shutdown from
        # the main program stream.

        # Temporary decision for shutdown server inside threading.
        self.server._BaseServer__shutdown_request = True


class MetadiskTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.metadisk_python_interpreter = sys.executable

    def setUp(self):
        HOST, PORT = 'localhost', 5000
        socketserver.TCPServer.allow_reuse_address = True
        server = socketserver.TCPServer((HOST, PORT), MyRequestHandler)
        _thread.start_new_thread(server.serve_forever, ())
        # delay for running server.
        time.sleep(2)

    @unittest.skip('yet unrealized action on server for this test')
    def test_info(self):
        with os.popen('%s metadisk.py info' %
                              self.metadisk_python_interpreter) as file:
            info_response = file.read()
        info_dict = json.loads(info_response[4:-1])

        self.assertEqual(info_dict.keys(),
                         dict.fromkeys(('bandwidth', 'storage', 'public_key'),
                                       None).keys())
        self.assertEqual(info_dict['bandwidth'].keys(),
                         dict.fromkeys(('current', 'limits', 'total'),
                                       None).keys())
        self.assertEqual(info_dict['bandwidth'].keys(),
                         dict.fromkeys(('current', 'limits', 'total'),
                                       None).keys())
        for item in info_dict['bandwidth'].keys():
            for key in ["incoming", "outgoing"]:
                self.assertTrue(key in info_dict['bandwidth'][item])
        self.assertEqual(info_dict["storage"].keys(),
                         dict.fromkeys(("capacity", "max_file_size", "used"),
                                       None).keys())

    def test_files(self):
        # first call must return an empty list of files
        with os.popen('%s metadisk.py files' %
                              self.metadisk_python_interpreter) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response, [])

    @unittest.skip('yet unrealized action on server for this test')
    def test_upload(self):
        with os.popen('%s metadisk.py upload metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response['file_role'], '001')

        with os.popen('%s metadisk.py files' %
                              self.metadisk_python_interpreter) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response, [upload_response['data_hash'], ])

        with os.popen('%s metadisk.py upload test_metadisk.py --file_role 002'
                              % self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response['file_role'], '002')

    @unittest.skip('yet unrealized action on server for this test')
    def test_download(self):
        with os.popen('%s metadisk.py upload metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        os.system('%s metadisk.py download %s' % (
                self.metadisk_python_interpreter,
                upload_response['data_hash']))
        with open(upload_response['data_hash'], 'rb') as file:
            ensure_hash = sha256(file.read()).hexdigest()
        self.assertEqual(upload_response['data_hash'], ensure_hash)
        os.remove(ensure_hash)

        rename_file = 'test_download_file'
        os.system('%s metadisk.py download %s --rename_file %s' % (
                self.metadisk_python_interpreter, upload_response['data_hash'],
                rename_file,))
        with open(rename_file, 'rb') as file:
            ensure_hash = sha256(file.read()).hexdigest()
        self.assertEqual(upload_response['data_hash'], ensure_hash)
        os.remove(rename_file)

    @unittest.skip('yet unrealized action on server for this test')
    def test_audit(self):
        with os.popen('%s metadisk.py upload metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        with open('metadisk.py', 'rb') as file:
            file_data = file.read()
        challenge_seed = sha256(b'seed').hexdigest()
        challenge_response = sha256(
            file_data + challenge_seed.encode()).hexdigest()
        with os.popen('%s metadisk.py audit %s %s' % (
                self.metadisk_python_interpreter, upload_response['data_hash'],
                challenge_seed,))as file:
            audit_response = json.loads(file.read()[4:-1])
        self.assertEqual(challenge_response,
                         audit_response['challenge_response'])


if __name__ == '__main__':
    unittest.main()
