import sys
import os
import os.path
import requests

from hashlib import sha256

# 2.x/3.x compliance logic
if sys.version_info.major == 3:
    from urllib.parse import urljoin
else:
    from urlparse import urljoin


def audit(url_base, sender_key, btctx_api, file_hash, seed):
    """
    It performs an request to the server with a view of calculating
    the SHA-256 hash of a file plus some seed.
    It will return the response object with information about the server-error
    when such has occurred.

    :param url_base:  (str) URL string which defines the server will be used.
    :param sender_key: (str) unique secret key which will be used for the
                        generating credentials required by the access to the
                        server.
    :param btctx_api:  instance of the BtcTxStore class from btctxstore module.
                        It will be used to generate credentials for server
                        access. (https://pypi.python.org/pypi/btctxstore/4.6.0)
    :param file_hash:  (str) hash-name of the file you are going to audit.
    :param seed: (str) should be a SHA-256 hash of that you would like to add
                        to the file data to generate a challenge response.
    :return: response: (<class 'requests.models.Response'>) response instance
                        with the results of challenge or with information about
                        the server issue.
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


def download(url_base, sender_key, btctx_api, file_hash,
             rename_file=None, decryption_key=None, link=False):
    """
    It performs the downloading of the file from the server
    by the given "file_hash".
    If "link=True" will return GET-request URL-string instead of performing the
    download, so you can use it like a simple URL address and download it
    through the browser.
        None: The "link=True" case implies non-authenticated access to the
        file, available only for files with such values of "roles": 101, 001

    Will return the response object with information about the server-error
    when such has occurred.

    :param url_base:  (str) URL string which defines the server will be used.
    :param sender_key: (str) unique secret key which will be used for the
                        generating credentials required by the access to the
                        server.
    :param btctx_api:  instance of the BtcTxStore class from btctxstore module.
                        It will be used to generate credentials for server
                        access. (https://pypi.python.org/pypi/btctxstore/4.6.0)
    :param file_hash:  (str) hash-name of the file on the remote server.
    :param rename_file:  (str) defines new name of the file after downloading.
    :param decryption_key:  (str)  key value which will be used to decrypt file
                            on the server before the downloading (if allowed by
                            the role).
    :param link: (boll) If True is given, function will generate and return
                        the appropriate GET URL-string instead of performing
                        the downloading process.
    :return:
        <file_path>: (str) will return full path to the file if downloaded
                            done successfully.
        <GET URL-string>: (str) if "link=True" will return GET-request
                            URL-string, instead of processing the downloading.
        response_object: (<class 'requests.models.Response'>) with information
                            about the occurred error on the server while
                            the downloading.
    """
    url_for_requests = urljoin(url_base, '/api/files/' + file_hash)

    params = {}
    if decryption_key:
        params['decryption_key'] = decryption_key

    if rename_file:
        params['file_alias'] = rename_file

    data_for_requests = dict(params=params)
    if link:
        request = requests.Request('GET', url_for_requests,
                                   **data_for_requests)
        request_string = request.prepare()
        return request_string.url

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
        file_name = os.path.join(os.getcwd(),
                                 response.headers['X-Sendfile'])

        with open(file_name, 'wb') as fp:
            fp.write(response.content)
        return file_name
    else:
        return response


def upload(url_base, sender_key, btctx_api, file, file_role):
    """
    Core method of the METATOOL API which uploads local file to the server.
    Max size of file is determined by the server. In the most of cases it is
    restricted by the 128 MB.
    Will return the response object with information about the server-error
    when such has occurred.

    :param url_base:  (str) URL string which defines the server will be used.
    :param sender_key: (str) unique secret key which will be used for the
                        generating credentials required by the access to the
                        server.
    :param btctx_api:  instance of the BtcTxStore class from btctxstore module.
                        It will be used to generate credentials for server
                        access. (https://pypi.python.org/pypi/btctxstore/4.6.0)
    :param file:  file object opened in the 'rb' mode,
                        which will be uploaded to the server.
    :param file_role:  (str)  three numbers string which define future
                        behavior of the file on the server. See more about
                        it in the documentation.
    :return: response: (<class 'requests.models.Response'>) response instance.
    """
    files_header = {'file_data': file}
    data_hash = sha256(file.read()).hexdigest()
    file.seek(0)
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
    return response


def files(url_base):
    """
    It executes a request to the "Node" server and returns response object
    with json-string - the list of hashes of downloaded files.

    :param url_base: (str) URL string which defines the server
                        that will be used.
    :return: response object
    """
    response = requests.get(urljoin(url_base, '/api/files/'))
    return response


def info(url_base):
    """
    It executes a request to the "Node" server and returns response object
    with json-string - the information about server state.

    :param url_base: (str) URL string which defines the server
                        that will be used.
    """
    response = requests.get(urljoin(url_base, '/api/nodes/me/'))
    return response
