"""
This module represents MetaTool API - set of functions purposed for
interaction with MetaCore cloud servers. Each function provides specific
type of operation with the MetaCore server. Look through the functions for
detailed specification.
"""
import sys
import os
import os.path
import requests
import tempfile
import shutil
import json
import binascii
from hashlib import sha256

import file_encryptor

# 2.x/3.x compliance logic
if sys.version_info.major == 3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


def audit(url_base, sender_key, btctx_api, file_hash, seed):
    """It make an request to the server with a view of calculating
    the SHA-256 hash of a file plus some seed.
    Return the response object with information about the server-error
    when such has occurred.

    :param url_base: URL string which defines the server will be used
    :type url_base: string

    :param sender_key: unique secret key which will be used for the
        generating credentials required by the access to the server
    :type sender_key: string

    :param btctx_api: instance of the ``BtcTxStore`` class which will be used
        to generate credentials for the server access
    :type btctx_api: btctxstore.BtcTxStore object

    :param file_hash: hash-name of the file you are going to audit
    :type file_hash: string

    :param seed: (str) should be a SHA-256 hash of that you would like to add
        to the file data to generate a challenge response
    :type seed: string

    :returns: response instance with the results of challenge or with
        information about the server issue
    :rtype: requests.models.Response object
    """
    signature = btctx_api.sign_unicode(sender_key, file_hash)
    sender_address = btctx_api.get_address(sender_key)
    response = requests.post(
        urljoin(url_base, '/api/audit/'),
        data={
            'data_hash': file_hash,
            'challenge_seed': seed,
        },
        headers={
            'sender-address': sender_address,
            'signature': signature,
        }
    )
    return response


def download(url_base, file_hash, sender_key=None, btctx_api=None,
             rename_file=None, decryption_key=None, link=False):
    """
    It performs the downloading of the file from the server
    by the given ``file_hash``.
    If ``link=True`` will return GET-request URL-string instead of download,
    so you can use it like a simple URL address and download file through the
    browser.

    :note: The "link=True" case implies non-authenticated access to the
        file, available only for files with such values of ``roles``: 101, 001

    Will return the response object with information about the server-error,
    when such has occurred.

    :param url_base: URL-string, which defines the server, that will be used

        :note: should be used the generic URI syntax, i.e.:
            ``http://node2.metadisk.org/``

    :type url_base: string

    :param sender_key: unique secret key which will be used for the
        generating credentials required by the access to the server

        (optional, default: None)
    :type sender_key: string

    :param btctx_api: instance of the ``BtcTxStore`` class which will be used
        to generate credentials for the server access

        (optional, default: None)
    :type btctx_api: btctxstore.BtcTxStore object

    :param file_hash: hash-name of the file you are going to audit
    :type file_hash: string

    :param rename_file: defines new name of the file after downloading

        (optional, default: None)
    :type rename_file: string

    :param decryption_key: key value, hexlify from bytes, which will be used to
        decrypt file locally, or used as a GET-parameter, when ``link==True``

        (optional, default: None)
    :type decryption_key: string

    :param link: if ``True``, function doesn't perform the downloading, but
        generate appropriate GET URL-string instead

        (optional, default: False)
    :type link: boolean

    :returns: full path to the file, if download done successfully

        :rtype: string
    :returns: if ``link=True``, will return GET-request
        URL-string, instead of processing the downloading

        :rtype: string
    :returns: object with information about the occurred error on the server,
        while the downloading

        :rtype: requests.models.Response object
    """
    url_for_requests = urljoin(url_base, '/api/files/' + file_hash)

    # dict where to collect GET parameters
    params = {}
    if rename_file:
        params['file_alias'] = rename_file

    data_for_requests = dict(params=params)
    if link:
        if decryption_key:
            params['decryption_key'] = decryption_key
        request = requests.Request('GET', url_for_requests,
                                   **dict(params=params))
        request_string = request.prepare()
        return request_string.url

    if sender_key or btctx_api:
        if not (sender_key and btctx_api):
            raise TypeError("arguments 'sender_key' and 'btctx_api' "
                            "should be provided together")
        else:
            signature = btctx_api.sign_unicode(sender_key, file_hash)
            sender_address = btctx_api.get_address(sender_key)
            data_for_requests['headers'] = {
                'sender-address': sender_address,
                'signature': signature,
            }

    response = requests.get(
        url_for_requests,
        **data_for_requests
    )
    if response.status_code == 200:
        file_name = os.path.join(os.path.abspath(
                response.headers['X-Sendfile']))
        download_dir = os.path.dirname(file_name)
        if download_dir:
            if not os.path.exists(download_dir):
                os.makedirs(download_dir)
        with open(file_name, 'wb') as fp:
            fp.write(response.content)
        if decryption_key:
            bytes_decryption_key = binascii.unhexlify(decryption_key)
            file_encryptor.convergence.decrypt_file_inline(
                        file_name, bytes_decryption_key)
        return file_name
    else:
        return response


def upload(url_base, sender_key, btctx_api, file_, file_role, encrypt=False):
    """
    Upload local file to the server. Max size of file is determined by the
    server. In the most of cases it is restricted by the 128 MB.
    Return the response object with ``file_hash`` and ``file_role`` when
    have done successfully or the server-error when such has occurred.

    The **encrypted file** is preferred, but not forced, way to serve files
    on the MetaCore server, so uploading supports the **encryption**.
    When ``encrypt=True``, to the returned JSON will be added the
    ``decryption_key``. It is an "hexadecimalised" value of the bytes
    ``decryption_key`` value.

    :param url_base: URL-string which defines the server will be used
    :type url_base: string

    :param sender_key: unique secret key which will be used for the
        generating credentials required by the access to the server
    :type sender_key: string

    :param btctx_api: instance of the ``BtcTxStore`` class which will be used
        to generate credentials for the server access
    :type btctx_api: btctxstore.BtcTxStore object

    :param encrypt: this is a flag which defines, will be the encryption done

        (optional, default: False)
    :type encrypt: boolean

    :param file_: file object which will be uploaded to the server
    :type file_: file object opened in the 'rb' mode

    :param file_role: string of three numbers which define future
        behavior of the file on the server (look more it in the documentation)
    :type file_role: string

    :returns: response instance with the results of uploading or with
        information about the server issue
    :rtype: requests.models.Response object
    """
    decryption_key = None
    temp_dir_name = ''
    try:
        if encrypt:
            source_file_name = file_.name
            temp_dir_name = tempfile.mkdtemp(prefix='metatool.')
            shutil.copy2(source_file_name, temp_dir_name)
            temp_file_name = os.path.join(
                temp_dir_name,
                os.path.split(source_file_name)[-1])
            decryption_key = file_encryptor.convergence.encrypt_file_inline(
                        temp_file_name, None)
            file_.close()
            file_ = open(temp_file_name, 'rb')

        file_.seek(0)
        files_header = {'file_data': file_}
        data_hash = sha256(file_.read()).hexdigest()
        file_.seek(0)
        sender_address = btctx_api.get_address(sender_key)
        signature = btctx_api.sign_unicode(sender_key, data_hash)

        response = requests.post(
                urljoin(url_base, '/api/files/'),
                data={
                    'data_hash': data_hash,
                    'file_role': file_role,
                },
                files=files_header,
                headers={
                    'sender-address': sender_address,
                    'signature': signature,
                }
        )
        file_.close()
        if decryption_key and response.status_code == 201:
            decryption_key = binascii.hexlify(decryption_key)
            if sys.version_info.major == 3:
                decryption_key = decryption_key.decode()
            success_content_dict = response.json()
            success_content_dict['decryption_key'] = decryption_key
            new_content = json.dumps(success_content_dict, indent=2,
                                     sort_keys=True)
            response._content = new_content.encode('ascii')
    finally:
        shutil.rmtree(temp_dir_name, ignore_errors=True)

    return response


def files(url_base):
    """
    It executes a request to the "Node" server and returns response object
    with json-string - the list of hashes of downloaded files.

    :param url_base: URL-string which defines the server will be used
    :type url_base: string

    :returns: response instance with a list of string - hashes of files
        available on the server or with information about the server issue
    :rtype: requests.models.Response object
    """
    response = requests.get(urljoin(url_base, '/api/files/'))
    return response


def info(url_base):
    """
    It executes a request to the "Node" server and returns response object
    with json-string - the information about server application state.

    :param url_base: URL-string which defines the server will be used
    :type url_base: string

    :returns: response instance with node state information or with
        information about the server issue
    :rtype: requests.models.Response object
    """
    response = requests.get(urljoin(url_base, '/api/nodes/me/'))
    return response
