import os
import sys
import unittest

from requests.models import Response
from btctxstore import BtcTxStore
from hashlib import sha256
from metatool import core

if sys.version_info.major == 3:
    from unittest.mock import patch, Mock, call, mock_open
    from urllib.parse import urljoin
else:
    from mock import patch, Mock, call, mock_open
    from urlparse import urljoin

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
            '``requests.get()``'
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
            '``requests.get()``'
        )


class TestCoreDownload(unittest.TestCase):
    """
    Test case for the ``metatool.core.download()`` API function.
    """
    def setUp(self):
        self.post_patch = patch('requests.get')
        self.mock_post = self.post_patch.start()
        self.mock_post.return_value = Response()

    def tearDown(self):
        self.post_patch.stop()

    def test_bad_response(self):
        """
        Test of returning gotten response object when it's status is not 200.
        """
        test_url_address = 'http://test.url.com'
        file_hash = sha256(b'some test data').hexdigest()
        test_data_for_requests = dict(params={})

        download_call_result = core.download(test_url_address, file_hash)
        expected_calls = [call(
            urljoin(test_url_address, '/api/files/' + file_hash),
            **test_data_for_requests
        )]

        self.assertListEqual(
            self.mock_post.call_args_list,
            expected_calls,
            'In the download() function requests.post() calls are unexpected'

        )
        self.assertIs(
            self.mock_post.return_value,
            download_call_result,
            'Returned value must be the object returned by the '
            '``requests.get()``'
        )


