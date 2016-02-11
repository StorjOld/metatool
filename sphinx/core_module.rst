metatool.core module
====================

MetaTool API specification
--------------------------

.. automodule:: metatool.core
    :members:
    :undoc-members:
    :show-inheritance:

MetaTool API Guide
------------------

This part of the documentation gives thorough knowledge of the MetaTool API usage.

Introduction
""""""""""""

All API functions are placed in the ``metatool.core`` module, which is described on the `MetaTool API specification`_,
so here we'll look on their use.

To start using the MetaTool API you should get the source code from the repository_ and
either install the package with the ``python setup.py install`` command, or make sure that the directory nested the ``metatool`` package
is present at your ``sys.path``.

.. _repository: https://github.com/Storj/metatool.git

:Note: The ``metatool`` python package is not the same as root repository directory. The ``metatool`` package is the
    **metatool** subdirectory of this repository.

Let's try to use it just installed required packages - clone the repo, open it, check the requirements and try to import package::

    $ git clone https://github.com/Storj/metatool.git
    Cloning into 'metatool'...
    remote: Counting objects: 504, done.
    ...
    $ cd metatool
    $ pip install -r metatool/requirements.txt
    Ignoring mock: markers "python_version == '2.7'" don't match your environment
    Collecting btctxstore (from -r metatool/requirements.txt (line 2))
    Collecting requests (from -r metatool/requirements.txt (line 3))
    ...
    $ python
    Python 3.4.3 (default, Oct 14 2015, 20:28:29)
    [GCC 4.8.4] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import metatool
    >>> metatool.core.files('http://node3.metadisk.org').text
    '["1d5ae562cc38e3adcf01a062207c2894fb8d055cfcf8200c3854c77eb6965645",
    "e3ae2933e83015368e3eb72d6de99442bde5195ae317dc9591ad9feaabdaebc8"]'
    >>>

This is the simplest use o MetaTool API. We've imported package from the current working directory,
called the core ``files`` function with desired URL and look at the ``text`` attribute of the returned Response object.
Ass result we see some json string with hash-names of the files uploaded to the server.

Next we will look at all API function closely.

.. _common-arguments:

Review of common arguments
""""""""""""""""""""""""""

:url_base:
    Each API function require this argument to define the server to send a request.
    This is the ``string`` value in format ``'http://your.server.com'``

:btctx_api:
    This is an instance of the ``BtcTxStore`` class which will be used to generate credentials for the server access.

    btctxstore_ is a site-package Library to read/write data to bitcoin transaction outputs.
    The reason to pass this argument is that the core function prepares appropriate request's data for actions which
    can be done in the *test* and *real* mode. This mode is defined in passed ``BtcTxStore`` instance.

    .. _btctxstore: https://pypi.python.org/pypi/btctxstore

    :Note: The ``sender_key`` argument can be gained from this instance with ``create_key()`` method.

    To get this instance in the **test** mode you can use next command::

        btctx_api = BtcTxStore(testnet=True, dryrun=True)

..

:sender_key:
    Unique private key that will be used for the generating credentials, required by the access to the server.

    To get **test** ``sender_key`` you can use such a code::

        >>> from btctxstore import BtcTxStore
        >>> btctx_api = BtcTxStore(testnet=True, dryrun=True)
        >>> sender_key = btctx_api.create_key()
        >>> sender_key
        'cRVY2joZQcdSumgAmCNkKYfZQjGchsNdQK1hG1hviLjBGAr8Y2Fa'

..

:file_hash:
    It's a string value - hash of the file's data.
    This value is used like name of the file on the server.
    It ensures that the data passed to the endpoint has not been modified in transit.
    ``file_hash`` should be the SHA-256 hash of file_data.

    To get a proper ``file_hash`` from the file you can do next::

        >>> from hashlib import sha256
        >>>
        >>> # file object should be opened in the binary mode.
        >>> file = open('eggs.txt', 'rb')
        >>>
        >>> # check that the file object has the start stream position
        >>> # if it is used somewhere else.
        >>> file.seek(0)
        >>>
        >>> # get the proper data-hash
        >>> data_hash = sha256(file.read()).hexdigest()
        >>> data_hash
        >>> 'cRVY2joZQcdSumgAmCNkKYfZQjGchsNdQK1hG1hviLjBGAr8Y2Fa'

..

Status Info
"""""""""""

To do a quick glance at the nodes data usage use the ``metatoo.core.info()`` API function.
Only required argument is a host to use - string value in the next form::

    'http://your.host.org'

The return value is a response_ with the JSON object containing a data usage and limits for the node.
The same result you can get if you visit the **/api/nodes/me/** path of the node server in browser,
i.e. - http://node2.metadisk.org/api/nodes/me/.

.. _response: http://docs.python-requests.org/en/latest/api/#requests.Response

Here's an example of usage the ``metatool.core.info()`` API function::

    >>> import json
    >>> response = metatool.core.info('http://node2.metadisk.org/')
    >>> json.loads(response.text)
    {
      "bandwidth": {
        "current": {
          "incoming": 0,
          "outgoing": 0
        },
        "limits": {
          "incoming": null,
          "outgoing": null
        },
        "total": {
          "incoming": 0,
          "outgoing": 0
        }
      },
      "public_key": "13LWbTkeuu4Pz7nFd6jCEEAwLfYZsDJSnK",
      "storage": {
        "capacity": 524288000,
        "max_file_size": 924391,
        "used": 992874
      }
    }

..

File Info
"""""""""

You can get all files currently listed on the node by use the ``metatool.core.files()`` API function.
All are the same as in previous function - provide an URL and you get response_ with the JSON object,
but this time it's a list of hash-names of files available on the node. Use they for access to the files.
The same list will be represented if you visit http://your.host.org/api/files URL.


In example::

    >>> import json
    >>> response = metatool.core.files('http://node2.metadisk.org/')
    >>> json.loads(response.text)
    ['1d5ae562cc38e3adcf01a062207c2894fb8d055cfcf8200c3854c77eb6965645',
    '103de8978a393c6479a092ce22cf04a6dd8876039c53b66df8384f361f60163c',
    '6f9745658c158a8b61b340164c9b899f26afbc0d823f5e4d2d92872b53eda9b0',
    '6da1054eef20b8949622f2acc5a89c3243ff3b3d7aa8c2bb8fa5c04d15113c00',
    '1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e',
    '51484ac97ae37f52655160d714eb2c6ac56909aa2d170cd7812e01c35544db23']

..

POST Data
"""""""""

You can upload data via POST to an node with ``metatool.core.upload()`` function.
It require ``url_base``, ``sender_key``, ``btctx_api`` arguments, described at `Review of common arguments`_
and three original arguments:

:file:
    It's a file object, opened in the ``'rb'`` mode::

        # file object should be opened in the binary mode!
        file_obj = open('eggs.txt', 'rb')

    :Note: File should not be larger than 128 MB.

:file_role:
    It's a string of three numbers which define future behavior of the file on the server.
    For example, ``'001'`` would be a free public file that can be downloaded in plaintext.
    Look more at the :ref:`file-roles`.

    :Note: Be sure to use strings - if you pass the role like integer ``001``
        instead of ``'001'`` passed value will be ``1`` and upload will fail.
        It can confuse, because the integer value ``101`` will be processed fine.

:encrypt:
    The **encrypted file** is preferred, but not forced, way to serve files on the MetaCore server,
    so uploading supports the **encryption**.
    Default value ``encrypt=False``, which mean that the original file will be uploaded without changes.
    The ``True`` value runs the encryption logic. Temporary copy of your file will be encrypted
    and sent to the server; the additional item ``decryption_key`` will be added into the returned JSON.
    The value of ``decryption_key`` is a "hexadecimalised" value of the original bytes key.

It returns the response_ object with such a JSON string, when ``encrypt=False``::

    {
      "data_hash": "72937d081099a3326b05228e30e7ee8a0a05efac68ec2e8d3c6bf1ee4e5bda69",
      "file_role": "101"
    }

Let's look at the example:

    >>> import metatool
    >>> from btctxstore import BtcTxStore
    >>> import json
    >>> file_obj = open('some_file.txt', 'rb')
    >>> btctx_api = BtcTxStore(testnet=True, dryrun=True)
    >>> sender_key = btctx_api.create_key()
    >>> response = metatool.core.upload(
    ...     url_base='http://localhost:5000',
    ...     sender_key=sender_key,
    ...     btctx_api=btctx_api,
    ...     file=file_obj,
    ...     file_role='101'
    ... )
    >>> json.loads(response.text)
    {'file_role': '101', 'data_hash': '76a97c878c9c7a8321bb395c2b44d3fe2f8d81314d219b20138ed0e2dddd5182'}

:Note: reload of any file don't bring any effect - you will get the same response object,
    like you're doing it in the very first time, but transmission wouldn't be performed, and
    the old ``file_role`` **value will be retained**!!!

If you are going to upload some file in the encrypted form, set the ``encrypt=True``::

    ...
    >>> response = metatool.core.upload(
    ...     url_base='http://localhost:5000',
    ...     sender_key=sender_key,
    ...     btctx_api=btctx_api,
    ...     file=file_obj,
    ...     file_role='101',
    ...     encrypt=True
    ... )
    >>> json.loads(response.text)
    {"data_hash": "0c50ca846cba1140c1d1be3bdd1f9c10efed6e2692889e8520c73b96a548e998",
    "decryption_key": "5bfc58952efa86a89ab89cf6b605c9b8bfcd08d9b44e6070e761691ca1ed2b57",
    "file_role": "001"}

Download Data
"""""""""""""

``metatool.core.download()`` is the API MetaTool function, which downloads
data from the node server. Type of returned data is depends of download status -
if file is downloaded successfully returned data will be a **full path** to the saved file,
otherwise it will be a response_ object. Usually content of this response is a JSON
with some internal error status code::

    { "error_code": <internal_error_code> }

But, if you occasionally, or deliberately refer to any non-MetaCore server (i.e. http://google.com)
it can be any unpredictable response content.

Also, if the ``link`` optional argument will be provided like ``True``, instead of downloading
appropriate GET URL-request string will be returned to perform the downloading manually,
but downloading is available only for the non-authenticated access, defined for each file by the :ref:`file-roles`::

    >>> metatool.core.download(
    ...     url_base='http://node2.metadisk.org',
    ...     file_hash='1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e',
    ...     link=True
    ... )
    ...
    'http://node2.metadisk.org/api/files/1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e'

This mode of ``download()`` supports rendering of provided ``rename_file`` and ``decryption_key`` arguments::

    >>> metatool.core.download(
    ...     url_base='http://node2.metadisk.org',
    ...     file_hash='1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e',
    ...     rename_file='new_name.eggs',
    ...     decryption_key='5bfc58952efa86a89ab89cf6b605c9b8bfcd08d9b44e6070e761691ca1ed2b57',
    ...     link=True
    ... )
    'http://node2.metadisk.org/api/files/1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e?file_alias=new_name.eggs&decryption_key=5bfc58952efa86a89ab89cf6b605c9b8bfcd08d9b44e6070e761691ca1ed2b57'

This function have all of the `common-arguments`_ and three additional arguments:

:rename_file:
    Optional argument which is a string value that defines a new name and place where to save the file:

    - ``'new_name.txt'`` - downloaded file will be saved in the current work directory under this name
    - ``'../love_me_tender.mp3'`` - the file will be saved at the parend directory under given name
    - ``'/home/user/reptiles/eggs/spam.py'`` - file will be saved by the path regardless to the current
      directory, but recursively creating intermediate directories in given path.

    :Note: this operation can be restricted by the access-permissions (chmode_)

    By default file will be saved under the ``file_hash`` value as name in the current directory.

    .. _chmode: https://en.wikipedia.org/wiki/Chmod

:decryption_key:
    This is the optional argument - string which is a key to decrypt data in the course of downloading.

    :Note:
        MetaTool, in truth, decrypts files locally, regardless to the :ref:`file-roles`, but when
        you are downloading files manually from the server,
        (i.e. using gained URL-string, by passing the ``link=True`` to the ``metatool.core.download()`` on the browser)
        decryption is available only for the ``**1`` :ref:`file-roles` variants.

:link:
    It defines behaviour of the function:
    - ``False`` - the default value, when the function performs the downloading
    - ``True`` - function will generate the GET-request string for the given arguments

        :Note:
            ``True`` value implies free access to the file - the ``file_role`` should be
            one of ``101``, ``001``.

    Look for examples with ``link`` above.

The most simple way of use is provide only required positional arguments, but as mentioned above - it's available
only for the files with non-authenticated access (``'001', '101'`` role values)::

    >>> import metatool
    >>> metatool.core.download('http://node2.metadisk.org', '1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e')
    '/home/jeka/1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e'

To download files with other ``file_role`` you should pass ``sender_key`` and  ``btctx_api`` optional `common-arguments`_:

    >>> import metatool
    >>> from btctxstore import BtcTxStore
    >>> btctx_api = BtcTxStore(testnet=True, dryrun=True)
    >>> sender_key = btctx_api.create_key()
    >>> metatool.core.download(
    ...    url_base='http://localhost:5000',
    ...    file_hash="374522eb582f4773c9d92376c8aece5e7838375f69282d007ab5513034debf38",
    ...    sender_key=sender_key,
    ...    btctx_api=btctx_api
    ... )
    '/home/user/374522eb582f4773c9d92376c8aece5e7838375f69282d007ab5513034debf38'

Because of arguments ``sender_key`` and ``btctx_api`` in this function are optional, they can be omitted,
but you can't provide only one of them, they should be given at the same time.

If you try to download file with invalid credentials function will return response object with occurred error status::

    >>> response = metatool.core.download(
    ...    url_base='http://localhost:5000',
    ...    file_hash="374522eb582f4773c9d92376c8aece5e7838375f69282d007ab5513034debf38",
    ...    sender_key=lame_sender_key,
    ...    btctx_api=btctx_api
    ... )
    >>> print(response.text)
    {
      "error_code": 401
    }

File Audit
""""""""""

This function calculates the SHA-256 hash of a file plus some seed.
The reason for this is to ensure the existence of files on the server.

It requires all of the `common-arguments`_ and one original argument:

:seed:
    Challenge seed should be a SHA-256 hash of that you would like to add
    to the file data to generate a challenge response.

Here is an example of usage ``metatool.core.audit()``::

    >>> response = metatool.core.audit(
    ...     url_base='http://localhost:5000',
    ...     file_hash="374522eb582f4773c9d92376c8aece5e7838375f69282d007ab5513034debf38",
    ...     sender_key=sender_key,
    ...     btctx_api=btctx_api,
    ...     seed='19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b')
    ... )
    >>> print(response.text)
    {
      "challenge_response": "b766fa69c14d453433af277ea56a82253f7fd8fa17c286f028f154533ce60d56",
      "challenge_seed": "19b25856e1c150ca834cffc8b59b23adbd0ec0389e58eb22b3b64768098d002b",
      "data_hash": "374522eb582f4773c9d92376c8aece5e7838375f69282d007ab5513034debf38"
    }

..

-------------------

That's it, for the detailed specification look at the `MetaTool API specification`_ .
