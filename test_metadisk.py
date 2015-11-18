import os
import sys
import json
import unittest
import threading

from hashlib import sha256

from test_server import MyRequestHandler, ThreadedTCPServer


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

    def test_error_audit(self):
        """
        Test that `metadisk.py audit` return error when not valid data passed

        :return:
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

    def test_valid_json_data(self):
        """
        Test that `metadisk.py audit` return data when valid data passed
        :return:
        """
        data_hash = '3a6eb0790f39ac87c94f3856b2dd2c5d110e6811602261a9a923d3bb23adc8b7'
        challenge_seed = '19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b'

        expected_value = {
            "data_hash": data_hash,
            "challenge_seed": challenge_seed,
            "challenge_response": "a068cf9870a41ecc36e18be9277bc353f88e29ad8a1b2a778581b37453de7692"
        }

        with os.popen('{} metadisk.py audit {} {}'.format(
                self.metadisk_python_interpreter,
                data_hash,
                challenge_seed
        )) as audit:
            audit_response = json.loads(audit.read()[4:-1])
            self.assertEqual(expected_value, audit_response)


if __name__ == '__main__':
    unittest.main()
