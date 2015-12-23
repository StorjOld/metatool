import json
import os
import sys
import threading
import time
import unittest
from hashlib import sha256
from io import StringIO

if sys.version_info.major == 3:
    from urllib.parse import urlparse, parse_qs, urlencode
else:
    from urlparse import urlparse, parse_qs
    from urllib import urlencode

from metatool.tests.testing_server import MyRequestHandler, ThreadedTCPServer


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
        path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        os.chdir(path)

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
        file_data = b'some data in test file\r\n\r\nself-delete after the test'
        data_hash = sha256(file_data).hexdigest()
        with open('temporary_test_file', 'wb') as file:
            file.write(file_data)
        expected_value = {
            "data_hash": data_hash,
            "file_role": "001",
        }
        with os.popen('{} metadisk.py upload temporary_test_file'.format(
                self.metadisk_python_interpreter)) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response, expected_value)
        os.remove('temporary_test_file')

    def test_upload_set_file_role(self):
        """
        Test of uploading file on the server through
        "python metadisk.py upload setup.sh --file_role 002" command call.
        """
        file_data = b'some data in test file\r\n\r\nself-delete after the test'
        data_hash = sha256(file_data).hexdigest()
        with open('temporary_test_file', 'wb') as file:
            file.write(file_data)
        expected_value = {
            "data_hash": data_hash,
            "file_role": "002",
        }
        with os.popen(
            '{} metadisk.py upload temporary_test_file --file_role 002'.format(
                self.metadisk_python_interpreter)) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response['file_role'],
                         expected_value['file_role'])
        os.remove('temporary_test_file')

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

    def test_download_link(self):
        """
        Test for the '--link' argument. It should return GET url request string
        which can be used like an ordinary url string in the browser. Returned
        string must contain all additional argument passed after the download,
        line '--decryption_kay' and '--rename_file'.
        """
        data_hash = sha256(b'test_data').hexdigest()
        with os.popen('{} metadisk.py download {} --link'.format(
            self.metadisk_python_interpreter,
            data_hash
        )) as printed_data:
            request_url_string = printed_data.read().rstrip(os.linesep)
        url_object = urlparse(request_url_string)
        data_hash_from_url = url_object.path.split('/')[-1]
        self.assertEqual(data_hash, data_hash_from_url,
                         'unexpected "data_hash" value '
                         'in the returned url line'
        )

        sended_data = dict(
                decryption_key='my_key',
                file_alias='new_name.txt'
            )
        expected_url_get_dict = parse_qs(urlencode(sended_data))
        bash_command_template = """\
        {} metadisk.py download {} --decryption_key {} --rename_file {} --link
        """
        with os.popen(
            bash_command_template.format(
                self.metadisk_python_interpreter,
                data_hash,
                sended_data['decryption_key'],
                sended_data['file_alias'],
            )
        ) as printed_data:
            request_url_string = printed_data.read().rstrip(os.linesep)
        received_url_get_dict = parse_qs(urlparse(request_url_string).query)
        self.assertEqual(expected_url_get_dict, received_url_get_dict,
                         'unexpected "decryption_key" value in the returned '
                         'url line')



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

    def test_url_attribute_use(self):
        """
        Test of the "--url" optional argument. The "metadisk.py" must use this
        value like url of all responses.
        """
        host, port = 'localhost', 5467
        server = ThreadedTCPServer((host, port), MyRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Hiding of the server running logging. Excise next string if test is
        # failing to look at the errors of local server.
        sys.stderr = StringIO()
        with os.popen(
            '{} metadisk.py --url http://{}:{} info'.format(
                self.metadisk_python_interpreter, host, port)
        ) as file:
            info_response_status = file.read()[:3]
        sys.stderr.close()
        sys.stderr = sys.__stderr__  # Turn back the error stream output.
        self.assertEqual(
            info_response_status,
            '200',
            'the "response status" must be 200, like from this test-case local'
            ' server specified after "--url" optional argument!'
        )
        server.shutdown()
        server.server_close()

    def test_url_attribute_default(self):
        """
        Test of the default case for "metadisk.py" target server
        (without "--url" positional attribute).
        Might be just like the value in environment variable "MEATADISKSERVER"
        """
        host, port = 'localhost', 5467
        os.putenv('MEATADISKSERVER', 'http://{}:{}'.format(host, port))
        server = ThreadedTCPServer((host, port), MyRequestHandler)

        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()

        # Hiding of the server running logging. Excise next string if test is
        # failing to look at the errors of local server.
        sys.stderr = StringIO()
        with os.popen(
            '{} metadisk.py --url http://{}:{} info'.format(
                self.metadisk_python_interpreter, host, port)
        ) as file:
            info_response_status = file.read()[:3]
        sys.stderr.close()
        sys.stderr = sys.__stderr__  # Turn back the error stream output.
        self.assertEqual(
            info_response_status,
            '200',
            'the "response status" must be 200, like in this test-case'
            'local server specified at the "MEATADISKSERVER" env. variable!'
        )
        server.shutdown()
        server.server_close()


if __name__ == '__main__':
    unittest.main()
