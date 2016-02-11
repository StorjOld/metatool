import os
import sys
import unittest
import binascii

from requests.models import Response
from btctxstore import BtcTxStore
from hashlib import sha256
from metatool import core

if sys.version_info.major == 3:
    from unittest.mock import patch, Mock, call, mock_open
    from urllib.parse import urljoin, quote_plus, urlparse
else:
    from mock import patch, Mock, call, mock_open
    from urlparse import urljoin, urlparse
    from urllib import quote_plus

# make the parent tests package importable for the direct running
parent_dir = os.path.dirname(os.path.dirname(__file__))
if not parent_dir in sys.path:
    sys.path.insert(0, parent_dir)

class TestCoreFiles(unittest.TestCase):
    """
    Test-case for the ``metatool.core.files()`` API function.
    """

    @patch('requests.get')
    def test_use_url_argument(self, mock_requests_get):
        """
        Test of making the GET-request with provided ``url_base`` argument
        in the ``metatool.core.files()`` and returning gotten from
        ``requests.get()`` object.
        """
        test_url_address = 'http://test.url.com'
        mock_requests_get.return_value = Response()
        expected_calls = [call(test_url_address + '/api/files/')]

        returned_value = core.files(test_url_address)

        self.assertListEqual(
            mock_requests_get.call_args_list,
            expected_calls,
            'It should be only one call of the ``requests.get()`` with the '
            'test URL address'
        )
        self.assertIs(
            mock_requests_get.return_value,
            returned_value,
            'Returned value must be the object returned by the '
            '``requests.get()``'
        )


class TestCoreInfo(unittest.TestCase):
    """
    Test-case for the ``metatool.core.info()`` API function.
    """

    @patch('requests.get')
    def test_use_url_argument(self, mock_requests_get):
        """
        Test of making the GET-request with provided ``url_base`` argument
        in the ``metatool.core.info()`` and returning gotten from
        ``requests.get()`` object.
        """
        test_url_address = 'http://test.url.com'
        mock_requests_get.return_value = Response()
        expected_calls = [call(test_url_address + '/api/nodes/me/')]

        returned_value = core.info(test_url_address)

        self.assertListEqual(
            mock_requests_get.call_args_list,
            expected_calls,
            'It should be only one call of the ``requests.get()`` with the '
            'test URL address'
        )
        self.assertIs(
            mock_requests_get.return_value,
            returned_value,
            'Returned value must be the object returned by the '
            '``requests.get()``'
        )


class TestCoreUpload(unittest.TestCase):
    """
    Test of the ``metatool.core.upload()`` API function.
    """
    def setUp(self):
        self.post_patch = patch('requests.post')
        self.mock_post = self.post_patch.start()
        self.mock_post.return_value = Response()

    def tearDown(self):
        self.post_patch.stop()

    def test_core_upload(self):
        """
        Test of providing correct arguments to the ``requests.post()``
        and returning gotten response object.
        """
        # Test fixture
        full_file_path = os.path.join(os.path.dirname(__file__),
                                      'temporary_test_file')
        temp_file = open(full_file_path, 'wb')
        temp_file.write(b'some file content')
        temp_file.close()
        self.addCleanup(os.unlink, full_file_path)

        test_url_address = 'http://test.url.com'
        btctx_api = BtcTxStore(testnet=True, dryrun=True)
        sender_key = btctx_api.create_key()
        file_role = '111'
        with open(full_file_path, 'rb') as temp_file_obj:
            temp_file_obj.flush()
            temp_file_obj.seek(0)
            data_hash = sha256(temp_file_obj.read()).hexdigest()
            upload_call_result = core.upload(test_url_address, sender_key,
                                             btctx_api, temp_file_obj,
                                             file_role)
            expected_calls = [call(
                    urljoin(test_url_address, '/api/files/'),
                    data={
                        'data_hash': data_hash,
                        'file_role': file_role
                    },
                    files={'file_data': temp_file_obj},
                    headers={
                        'sender-address': btctx_api.get_address(sender_key),
                        'signature': btctx_api.sign_unicode(sender_key,
                                                            data_hash)
                    }
            )]

        self.assertListEqual(
            self.mock_post.call_args_list,
            expected_calls,
            'In the upload() function requests.post() calls are unexpected'

        )
        self.assertIs(
            self.mock_post.return_value,
            upload_call_result,
            'Returned value must be the object returned by the '
            '``requests.post()``'
        )


class TestCoreAudit(unittest.TestCase):
    """
    Test of the ``metatool.core.audit()`` API function.
    """
    def setUp(self):
        self.post_patch = patch('requests.post')
        self.mock_post = self.post_patch.start()
        self.mock_post.return_value = Response()

    def tearDown(self):
        self.post_patch.stop()

    def test_core_audit(self):
        """
        Test of providing correct arguments to the ``requests.post()``
        and returning gotten response object.
        """
        test_url_address = 'http://test.url.com'
        file_hash = sha256(b'some test data').hexdigest()
        seed = sha256(b'some test challenge seed').hexdigest()
        btctx_api = BtcTxStore(testnet=True, dryrun=True)
        sender_key = btctx_api.create_key()
        audit_call_result = core.audit(test_url_address, sender_key,
                                       btctx_api, file_hash, seed)

        expected_calls = [call(
                urljoin(test_url_address, '/api/audit/'),
                data={
                    'data_hash': file_hash,
                    'challenge_seed': seed,
                },
                headers={
                    'sender-address': btctx_api.get_address(sender_key),
                    'signature': btctx_api.sign_unicode(sender_key, file_hash),
                }
        )]
        self.assertListEqual(
            self.mock_post.call_args_list,
            expected_calls,
            'In the audit() function requests.post() calls are unexpected'
        )
        self.assertIs(
            self.mock_post.return_value,
            audit_call_result,
            'Returned value must be the object returned by the '
            '``requests.post()``'
        )


class TestCoreDownload(unittest.TestCase):
    """
    Test case for the ``metatool.core.download()`` API function.
    """
    def setUp(self):
        self.post_patch = patch('requests.get')
        self.mock_get = self.post_patch.start()

        # set common data for tests
        self.test_url_address = 'http://test.url.com'
        self.file_content = b'some test data'
        self.file_hash = sha256(self.file_content).hexdigest()
        self.test_data_for_requests = dict(params={})

        # initial filling the base response object
        self.mock_get.return_value = Mock()
        mock_response = self.mock_get.return_value
        mock_response.status_code = 200
        mock_response.headers = {'X-Sendfile': self.file_hash}
        mock_response.content = self.file_content

    def tearDown(self):
        self.post_patch.stop()

    def test_bad_response(self):
        """
        Test of returning gotten response object when it's status is not 200.
        """
        self.mock_get.return_value.status_code = 404
        download_call_result = core.download(self.test_url_address,
                                             self.file_hash)
        expected_calls = [call(
            urljoin(self.test_url_address, '/api/files/' + self.file_hash),
            **self.test_data_for_requests
        )]
        self.assertListEqual(
            self.mock_get.call_args_list,
            expected_calls,
            'In the download() function requests.get() calls are unexpected'
        )
        self.assertIs(
            self.mock_get.return_value,
            download_call_result,
            'Returned value must be the object returned by the '
            '``requests.get()``'
        )

    def test_good_response(self):
        """
        Test of returning path for downloaded file when response status is 200.
        """
        created_test_file = os.path.abspath(self.file_hash)
        self.addCleanup(os.unlink, created_test_file)
        download_call_result = core.download(self.test_url_address,
                                             self.file_hash)
        expected_calls = [call(
            urljoin(self.test_url_address, '/api/files/' + self.file_hash),
            **self.test_data_for_requests
        )]
        expected_return_string = created_test_file
        self.assertListEqual(
            self.mock_get.call_args_list,
            expected_calls,
            'In the download() function requests.get() calls are unexpected'
        )
        self.assertEqual(
            download_call_result,
            expected_return_string,
            "Returned value must be downloaded file's full path"
        )
        with open(self.file_hash, 'rb') as downloaded_file:
            self.assertEqual(
                downloaded_file.read(),
                self.file_content,
                "The content of downloaded file isn't correct"
            )

    def test_download_in_cwd(self):
        """
        Test of downloading file to the current dir by default - when saving
        under hash-name or given simple new name (without any directories
        in the name string)
        """
        tests_dir = os.path.abspath(os.path.dirname(__file__))

        # Test saving under the hash-name by default
        created_test_file = os.path.join(tests_dir, self.file_hash)
        self.addCleanup(os.unlink, created_test_file)
        with patch('os.getcwd', return_value=tests_dir):
            call_result = core.download(self.test_url_address, self.file_hash)
        self.assertEqual(call_result, created_test_file,
                         "Returned path to the saved file isn't correct")
        with open(created_test_file, 'rb') as downloaded_file:
            self.assertEqual(
                downloaded_file.read(),
                self.file_content,
                "The content of downloaded file isn't correct"
            )

        # Test saving under the new name
        self.doCleanups()
        new_file_name = 'TEMP_TEST_FILE.spam'
        self.mock_get.return_value.headers['X-Sendfile'] = new_file_name
        created_test_file = os.path.join(tests_dir, new_file_name)
        self.addCleanup(os.unlink, created_test_file)
        with patch('os.getcwd', return_value=tests_dir):
            call_result = core.download(self.test_url_address, self.file_hash,
                                        rename_file=new_file_name)
        self.assertEqual(call_result, created_test_file,
                         "Returned path to the saved file isn't correct")
        with open(created_test_file, 'rb') as downloaded_file:
            self.assertEqual(
                downloaded_file.read(),
                self.file_content,
                "The content of downloaded file isn't correct"
            )

    def test_download_by_full_path(self):
        """
        Test for saving file by the given full path.
        """
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        new_file_name = 'TEMP_TEST_FILE.spam'
        created_test_file = os.path.join(tests_dir, 'temp_intermediate_dir',
                                         new_file_name)
        self.mock_get.return_value.headers['X-Sendfile'] = created_test_file
        self.addCleanup(os.rmdir, os.path.dirname(created_test_file))
        self.addCleanup(os.unlink, created_test_file)
        call_result = core.download(self.test_url_address, self.file_hash,
                                    rename_file=created_test_file)
        self.assertEqual(call_result, created_test_file,
                         "Returned path to the saved file isn't correct")
        with open(created_test_file, 'rb') as downloaded_file:
            self.assertEqual(
                downloaded_file.read(),
                self.file_content,
                "The content of downloaded file isn't correct"
            )

    def test_download_by_relative_path(self):
        """
        Test for saving file by the given relative path.
        """
        tests_dir = os.path.abspath(os.path.dirname(__file__))
        new_file_name = 'TEMP_TEST_FILE.spam'
        relative_name = '../../{}'.format(new_file_name)
        created_test_file = os.path.join(tests_dir, new_file_name)
        self.mock_get.return_value.headers['X-Sendfile'] = relative_name
        self.addCleanup(os.unlink, created_test_file)
        with patch('os.getcwd', return_value=tests_dir + '/dir1/dir2/'):
            call_result = core.download(self.test_url_address, self.file_hash,
                                        rename_file=relative_name)
        self.assertEqual(call_result, created_test_file,
                         "Returned path to the saved file isn't correct")
        with open(created_test_file, 'rb') as downloaded_file:
            self.assertEqual(
                downloaded_file.read(),
                self.file_content,
                "The content of downloaded file isn't correct"
            )

    def test_not_provide_get_param(self):
        """
        Test of not providing ``decryption_key`` and ``file_alias``
        to the ``core.download()``.
        """
        # Test to run without GET parameters
        self.mock_get.return_value.status_code = 404
        core.download(self.test_url_address, self.file_hash)
        expected_calls = [call(
            urljoin(self.test_url_address, '/api/files/' + self.file_hash),
            **self.test_data_for_requests
        )]
        self.assertListEqual(
            self.mock_get.call_args_list,
            expected_calls,
            'Wrong arguments are passed to requests.get() when only "url_base"'
            ' and "file_hash" arguments are given to the core.download()'
        )

    @patch('core.file_encryptor.convergence.decrypt_file_inline')
    def test_provide_decryption_key(self, mock_decryptor):
        """
        Test of providing ``decryption_key`` to the ``core.download()``.
        """
        # Test to run with given ``decryption_key`` argument.
        self.mock_get.return_value.status_code = 200
        decryption_key = b'test 32 character long key......'
        decryption_key_hex = binascii.hexlify(decryption_key)
        self.test_data_for_requests = dict(params={})

        # Get a appropriate "builtin" module name for pythons 2/3
        # and mocking the builtin `open` function.
        if sys.version_info.major == 3:
            builtin_module_name = 'builtins'
        else:
            builtin_module_name = '__builtin__'
        with patch('{}.open'.format(builtin_module_name),
                   mock_open(), create=False):
            core.download(self.test_url_address, self.file_hash,
                          decryption_key=decryption_key_hex)

        # Test of args, passed to `requests.get()` in the `core.download()`.
        expected_request_args = [call(
            urljoin(self.test_url_address, '/api/files/' + self.file_hash),
            **self.test_data_for_requests
        )]
        self.assertListEqual(
            self.mock_get.call_args_list,
            expected_request_args,
            'Wrong arguments are passed to requests.get() when "url_base", '
            '"file_hash" and "decryption_key" arguments are given to the '
            'core.download()'
        )
        # Test of args, passed to
        # `core.file_encryptor.convergence.decrypt_file_inline()`
        # in the `core.download()`.
        expected_decryption_args = [call(
            os.path.join(os.path.abspath(self.file_hash)),
            decryption_key)]
        self.assertListEqual(
            mock_decryptor.call_args_list,
            expected_decryption_args,
            'Wrong call of the '
            'core.file_encryptor.convergence.decrypt_file_inline() inside '
            'the metatool.core.download() function.'
        )

    def test_provide_rename_file(self):
        """
        Test of providing ``file_alias`` to the ``core.download()``.
        """
        # Test to run with given ``file_alias`` argument
        self.mock_get.return_value.status_code = 404
        file_alias = 'some new name'
        self.test_data_for_requests = dict(params={
            'file_alias': file_alias
        })
        core.download(self.test_url_address, self.file_hash,
                      rename_file=file_alias)

        expected_request_args = [call(
            urljoin(self.test_url_address, '/api/files/' + self.file_hash),
            **self.test_data_for_requests
        )]

        self.assertListEqual(
            self.mock_get.call_args_list,
            expected_request_args,
            'Wrong arguments are passed to requests.get() when "url_base", '
            '"rename_file" and "file_hash" arguments are given '
            'to the core.download()'
        )

    @patch('core.file_encryptor.convergence.decrypt_file_inline')
    def test_provide_rename_file_and_decryption_key(self, mock_decryptor):
        """
        Test of providing ``file_alias`` to the ``core.download()``.
        """
        # Test to run with given ``file_alias`` argument.
        file_alias = 'some new name'
        decryption_key = b'test 32 character long key......'
        decryption_key_hex = binascii.hexlify(decryption_key)
        self.mock_get.return_value.status_code = 200
        self.mock_get.return_value.headers['X-Sendfile'] = file_alias
        self.test_data_for_requests = dict(params={
            'file_alias': file_alias,
        })
        # Get a appropriate "builtin" module name for pythons 2/3
        # and mocking the builtin `open` function.
        if sys.version_info.major == 3:
            builtin_module_name = 'builtins'
        else:
            builtin_module_name = '__builtin__'
        with patch('{}.open'.format(builtin_module_name),
                   mock_open(), create=False):
            core.download(self.test_url_address, self.file_hash,
                          rename_file=file_alias,
                          decryption_key=decryption_key_hex)
        expected_request_args = [call(
            urljoin(self.test_url_address, '/api/files/' + self.file_hash),
            **self.test_data_for_requests
        )]
        # Test of args, passed to `requests.get()` in the `core.download()`.
        self.assertListEqual(
            self.mock_get.call_args_list,
            expected_request_args,
            'Wrong arguments are passed to requests.get() when "url_base", '
            '"file_hash", "rename_file" and "decryption_key" arguments are '
            'given to the core.download()'
        )
        # Test of args, passed to
        # `core.file_encryptor.convergence.decrypt_file_inline()`
        # in the `core.download()`.
        expected_decryption_args = [call(
            os.path.join(os.path.abspath(file_alias)),
            decryption_key)]
        self.assertListEqual(
            mock_decryptor.call_args_list,
            expected_decryption_args,
            'Wrong call of the '
            'core.file_encryptor.convergence.decrypt_file_inline() inside '
            'the metatool.core.download() function.'
        )

    def test_link_argument(self):
        """
        Test of generating GET-query string when ``link`` argument is ``True``.
        """
        # test with no additional params

        call_return = core.download(
                self.test_url_address,
                self.file_hash,
                link=True
        )
        expected_return = '{}/api/files/{}'.format(self.test_url_address,
                                                   self.file_hash)
        self.assertEqual(
            call_return,
            expected_return,
            "unexpected URL-query string when link=True"
        )

        # test with ``rename_file``
        file_alias = 'some new name'
        call_return = core.download(
                self.test_url_address,
                self.file_hash,
                rename_file=file_alias,
                link=True
        )
        expected_return = dict(
            scheme='http',
            netloc='test.url.com',
            path='/api/files/' + self.file_hash,
            params='',
            query='file_alias={}'.format(quote_plus(file_alias)),
            fragment=''
        )
        parse_result = urlparse(call_return)
        tested_result = dict(
            ((key, getattr(parse_result, key)) for key in expected_return)
        )
        self.assertEqual(
            tested_result,
            expected_return,
            "unexpected URL-query string when link=True"
        )

        # test with the ``decryption_key``
        decryption_key = 'some key'
        call_return = core.download(
                self.test_url_address,
                self.file_hash,
                decryption_key=decryption_key,
                link=True
        )
        expected_return = dict(
            scheme='http',
            netloc='test.url.com',
            path='/api/files/' + self.file_hash,
            params='',
            query='decryption_key={}'.format(quote_plus(decryption_key)),
            fragment=''
        )
        parse_result = urlparse(call_return)
        tested_result = dict(
            ((key, getattr(parse_result, key)) for key in expected_return)
        )
        self.assertEqual(
            tested_result,
            expected_return,
            "unexpected URL-query string when link=True"
        )

    def test_together_sender_key_and_btctx_api(self):
        """
        Test of possibility to provide the ``sender_key`` and ``btctx_api``
        only together.
        """
        btctx_api = BtcTxStore(testnet=True, dryrun=True)
        sender_key = btctx_api.create_key()
        self.mock_get.return_value = Response()

        # test only "sender_key" given
        self.assertRaises(
            TypeError,
            core.download,
            *(self.test_url_address, self.file_hash),
            **{'sender_key': sender_key}
        )

        # test only "btctx_api" given
        self.assertRaises(
            TypeError,
            core.download,
            *(self.test_url_address, self.file_hash),
            **{'btctx_api': btctx_api}
        )

        # test of now exception when both args are given
        download_call_result = core.download(
            self.test_url_address,
            self.file_hash,
            sender_key=sender_key,
            btctx_api=btctx_api
        )
        self.assertIsInstance(download_call_result, Response,
                              'Must return a response object')

    def test_authenticate_headers_provide(self):
        """
        Test of preparing and providing credential headers when ``sender_key``
        and ``btctx_api`` are provided.
        """
        btctx_api = BtcTxStore(testnet=True, dryrun=True)
        sender_key = btctx_api.create_key()
        signature = btctx_api.sign_unicode(sender_key, self.file_hash)
        sender_address = btctx_api.get_address(sender_key)
        self.mock_get.return_value = Response()
        self.test_data_for_requests['headers'] = {
                'sender-address': sender_address,
                'signature': signature,
            }
        download_call_result = core.download(
            self.test_url_address,
            self.file_hash,
            sender_key=sender_key,
            btctx_api=btctx_api
        )
        expected_mock_calls = [call(
            urljoin(self.test_url_address, '/api/files/' + self.file_hash),
            **self.test_data_for_requests
        )]

        self.assertListEqual(
            self.mock_get.call_args_list,
            expected_mock_calls,
            'In the download() function requests.get() calls are unexpected'
        )
        self.assertIsInstance(download_call_result, Response,
                              'Must return a response object')
