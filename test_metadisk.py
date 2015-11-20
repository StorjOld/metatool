import os
import sys
import json
import unittest
import threading
import time

from hashlib import sha256
from io import StringIO
from testing_server import MyRequestHandler, ThreadedTCPServer
from http.server import BaseHTTPRequestHandler


class MetadiskTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.metadisk_python_interpreter = sys.executable
        host, port = 'localhost', 5000
        ThreadedTCPServer.allow_reuse_address = True
        cls.server = ThreadedTCPServer((host, port), MyRequestHandler)

        server_thread = threading.Thread(target=cls.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Set the test server address like an environment variable which will
        # be used by the metadisk.py whilst the testing.
        os.environ['MEATADISKSERVER'] = 'http://{}:{}'.format(host, port)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_info(self):
        """
        Testing of getting right response from the "python metadisk.py info"
        command call.
        """
        expected_value = {
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
        with os.popen('{} metadisk.py info'.format(
                self.metadisk_python_interpreter)) as file:
            info_response = json.loads(file.read()[4:-1])

        self.assertEqual(info_response, expected_value)

    def test_files_empty_result(self):
        """
        Test for getting the empty list of served files.
        Must be called first, just before the "test_files_filled_result()"
        test case
        """
        expected_value = []
        with os.popen('{} metadisk.py files'.format(
                self.metadisk_python_interpreter)) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response, expected_value,
                         'command "python metadisk.py files" must return '
                         'must receive an empty list')

    def test_files_filled_result(self):
        """
        Testing for receiving the filled list of files from the server.
        Need to be called after "test_files_empty_result()" test case.
        """
        expected_value = [1, 2]
        with os.popen('{} metadisk.py files'.format(
                self.metadisk_python_interpreter)) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response, expected_value,
                         'command "python metadisk.py files" now must return '
                         'the {} list'.format(expected_value))

    def test_upload_simple_call(self):
        """
        Test of uploading file on the server through
        "python metadisk.py upload setup.sh" command call.
        """
        with open('setup.sh', 'rb') as file:
                data_hash = sha256(file.read()).hexdigest()

        expected_value = {
            "data_hash": data_hash,
            "file_role": "001",
        }
        with os.popen('{} metadisk.py upload setup.sh'.format(
                self.metadisk_python_interpreter)) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response, expected_value)

    def test_upload_set_file_role(self):
        """
        Test of uploading file on the server through
        "python metadisk.py upload setup.sh --file_role 002" command call.
        """
        with open('setup.sh', 'rb') as file:
                data_hash = sha256(file.read()).hexdigest()

        expected_value = {
            "data_hash": data_hash,
            "file_role": "002",
        }
        with os.popen(
                '{} metadisk.py upload setup.sh --file_role 002'.format(
                    self.metadisk_python_interpreter)) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response['file_role'],
                         expected_value['file_role'])

    def test_download_error(self):
        """
        Test that `metadisk.py download` return error if passed
        not valid data_hash
        """
        data_hash = 'test_not_valid_data_hash'
        expected_value = {'error_code': 101}
        with os.popen('{} metadisk.py download {}'.format(
            self.metadisk_python_interpreter,
            data_hash
        )) as download:
            download_response = json.loads(download.read()[4:-1])

            self.assertEqual(expected_value, download_response)

    def test_download_valid_data_hash(self):
        """
        Test that `metadisk.py download` return data if passed valid data
        """
        data_hash = 'test_valid_data_hash'
        test_file_name = 'TEST_FILE_NAME'
        expected_value = b'TEST_DATA'
        with os.popen('{} metadisk.py download {}'.format(
            self.metadisk_python_interpreter,
            data_hash
        )):
            counter = 0

            while not os.path.exists(test_file_name) or counter > 10:
                time.sleep(1)
                counter += 1

            self.assertTrue(os.path.isfile(test_file_name))
            with open(test_file_name, 'rb') as file:
                downloaded_file_data = file.read()[:-1]
            self.assertEqual(expected_value,
                             downloaded_file_data)
            os.remove(test_file_name)

    def test_download_rename_file(self):
        """
        Test that `metadisk.py download` with `--rename_file` return
        file with given_name
        """
        data_hash = 'test_valid_data_hash'
        test_file_name = 'DIFFERENT_TEST_FILE_NAME'
        with os.popen('{} metadisk.py download {} --rename_file {}'.format(
            self.metadisk_python_interpreter,
            data_hash,
            test_file_name
        )):
            counter = 0

            while not os.path.exists(test_file_name) or counter > 10:
                time.sleep(1)
                counter += 1

            self.assertTrue(os.path.isfile(test_file_name))
            os.remove(test_file_name)

    def test_download_decryption_key(self):
        """
        Test that `metadisk.py download` with `--decryption_key`
        return file with given_name
        """
        data_hash = 'test_valid_data_hash'
        test_file_name = 'TEST_FILE_NAME'
        decryption_key = 'some_test_decryption_key'
        expected_value = b'TEST_DATA'
        with os.popen('{} metadisk.py download {} --decryption_key {}'.format(
            self.metadisk_python_interpreter,
            data_hash,
            decryption_key
        )):
            counter = 0

            while not os.path.exists(test_file_name) or counter > 10:
                time.sleep(1)
                counter += 1

            self.assertTrue(os.path.isfile(test_file_name))
            with open(test_file_name, 'rb') as file:
                downloaded_file_data = file.read()[:-1]
            self.assertEqual(expected_value,
                             downloaded_file_data)
            os.remove(test_file_name)

    def test_error_audit(self):
        """
        Test that `metadisk.py audit` return error when not valid data passed
        """
        data_hash = 'test_not_valid_data_hash'
        challenge_seed = 'test_not_valid_challenge_seed'
        expected_value = {'error_code': 102}

        with os.popen('{} metadisk.py audit {} {}'.format(
                self.metadisk_python_interpreter,
                data_hash,
                challenge_seed
        )) as audit:
            audit_response = json.loads(audit.read()[4:-1])
            self.assertEqual(expected_value, audit_response)

    def test_audit_valid_json_data(self):
        """
        Test that `metadisk.py audit` return data when valid data passed
        """
        data_hash = '3a6eb0790f39ac87c94f3856b2dd2c5d'\
                    '110e6811602261a9a923d3bb23adc8b7'
        challenge_seed = '19b25856e1c150ca834cffc8b59b23ad'\
                         'bd0ec0389e58eb22b3b64768098d002b'

        expected_value = {
            "data_hash": data_hash,
            "challenge_seed": challenge_seed,
            "challenge_response": "a068cf9870a41ecc36e18be9277bc353"
                                  "f88e29ad8a1b2a778581b37453de7692"
        }

        with os.popen('{} metadisk.py audit {} {}'.format(
                self.metadisk_python_interpreter,
                data_hash,
                challenge_seed
        )) as audit:
            audit_response = json.loads(audit.read()[4:-1])
            self.assertEqual(expected_value, audit_response)

    def test_url_attribute(self):
        """
        Test of the "--url" optional argument. The "metadisk.py" must use this
        value like url of all responses.
        """
        host, port = 'localhost', 5467
        server = ThreadedTCPServer((host, port), BaseHTTPRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        with os.popen(
            '{} metadisk.py info --url http://{}:{}'.format(
                self.metadisk_python_interpreter, host, port)
        ) as file:
            info_response_status = file.read()[:3]
        self.assertEqual(
            info_response_status,
            '501',
            'the "response status" must be 501, like from this test-case local'
            ' server specified after "--url" optional argument!'
        )
        server.shutdown()
        server.server_close()

if __name__ == '__main__':
    unittest.main()
