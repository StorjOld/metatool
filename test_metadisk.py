import os
import sys
import json
import unittest
import subprocess
import signal
import time
import urllib.error, urllib.request

from hashlib import sha256


class MetadiskTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.storj_python_interpreter = (
            '/home/jeka/PycharmProjects/'
            'anvil8/storj/venv/bin/python'
        )
        cls.metadisk_python_interpreter = sys.executable

    def setUp(self):
        # temporary step purposed for cleaning "storj" git repository
        os.system('cd ../storj/; git clean -f; git checkout -- .')
        # running local storj server for each test separately
        self.child = subprocess.Popen(
            [self.storj_python_interpreter, '../storj/storj.py'],
            preexec_fn=os.setsid
        )
        for item in range(3):

            try:
                urllib.request.urlopen('http://localhost:5000/',
                                   timeout=15)
                break
            except urllib.error.URLError:
                if item == 2:
                    self.tearDown()
                    self.fail("test can't connect to the server of the app! "
                              "check out your connection and run test again.")
                time.sleep(2)


    def tearDown(self):
        # killing storj server
        os.killpg(self.child.pid, signal.SIGTERM)
        # cleanup after storj-server run
        os.system('cd ../storj/; git clean -f; git checkout -- .')


    def test_info(self):
        with os.popen('%s metadisk.py info' %
                              self.metadisk_python_interpreter) as file:
            info_response = file.read()
        info_dict = json.loads(info_response[4:-1])

        self.assertEqual(
            info_dict.keys(),
            dict.fromkeys(('bandwidth', 'storage', 'public_key'), None).keys())
        self.assertEqual(
            info_dict['bandwidth'].keys(),
            dict.fromkeys(('current', 'limits', 'total'), None).keys())
        self.assertEqual(
            info_dict['bandwidth'].keys(),
            dict.fromkeys(('current', 'limits', 'total'), None).keys())
        for item in info_dict['bandwidth'].keys():
            for key in ["incoming", "outgoing"]:
                self.assertTrue(key in info_dict['bandwidth'][item])
        self.assertEqual(
            info_dict["storage"].keys(),
            dict.fromkeys(("capacity", "max_file_size", "used"), None).keys())


    def test_files(self):
        # first call must return an empty list of files
        with os.popen('%s metadisk.py files' %
                              self.metadisk_python_interpreter) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response, [])

        # now the list must contain one file
        with os.popen('%s metadisk.py upload metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response_1 = json.loads(file.read()[4:-1])
        with os.popen('%s metadisk.py files' %
                              self.metadisk_python_interpreter) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response, [upload_response_1['data_hash'], ])

        # and now the list must contain two files
        with os.popen('%s metadisk.py upload test_metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response_2 = json.loads(file.read()[4:-1])
        with os.popen('%s metadisk.py files' %
                              self.metadisk_python_interpreter) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response,
                         [upload_response_1['data_hash'],
                          upload_response_2['data_hash'],])


    def test_upload(self):
        with os.popen('%s metadisk.py upload metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response['file_role'], '001')

        with os.popen('%s metadisk.py files' %
                              self.metadisk_python_interpreter) as file:
            files_response = json.loads(file.read()[4:-1])
        self.assertEqual(files_response, [upload_response['data_hash'], ])

        with os.popen('%s metadisk.py upload test_metadisk.py --file_role 002' %
                              self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        self.assertEqual(upload_response['file_role'], '002')


    def test_download(self):
        with os.popen('%s metadisk.py upload metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        with os.popen(
            '%s metadisk.py download %s' % (
                self.metadisk_python_interpreter,
                upload_response['data_hash']
            )
        ): pass
        with open(upload_response['data_hash'], 'rb') as file:
            ensure_hash = sha256(file.read()).hexdigest()
        self.assertEqual(upload_response['data_hash'], ensure_hash)
        os.remove(ensure_hash)

        rename_file = 'test_download_file'
        with os.popen(
            '%s metadisk.py download %s --rename_file %s' %
                (
                    self.metadisk_python_interpreter,
                    upload_response['data_hash'],
                    rename_file,
                )
            ): pass
        with open(rename_file, 'rb') as file:
            ensure_hash = sha256(file.read()).hexdigest()
        self.assertEqual(upload_response['data_hash'], ensure_hash)
        os.remove(rename_file)

    def test_audit(self):
        with os.popen('%s metadisk.py upload metadisk.py' %
                              self.metadisk_python_interpreter) as file:
            upload_response = json.loads(file.read()[4:-1])
        with open('metadisk.py', 'rb') as file:
            file_data = file.read()
        challenge_seed = sha256(b'seed').hexdigest()
        challenge_response = sha256(
            file_data + challenge_seed.encode()
        ).hexdigest()
        with os.popen(
            '%s metadisk.py audit %s %s' %
                (
                    self.metadisk_python_interpreter,
                    upload_response['data_hash'],
                    challenge_seed,
                )
            )as file:
            audit_response = json.loads(file.read()[4:-1])
        self.assertEqual(challenge_response, audit_response['challenge_response'])


if __name__ == '__main__':
    unittest.main()
