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

All API functions are placed in the ``metatool.core`` module which is described on the `MetaTool API specification`_,
so here we'll look on their use.

To start using the MetaTool API you should get the source code from the repository_ and
either install the package with the ``python setup.py install`` command or make sure that the directory nested the ``metatool`` package
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
        >>> btctx_api = btctxstore.BtcTxStore(testnet=True, dryrun=True)
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
The same result you can get if you visit node server on the server by the **api/nodes/me/** on the browser,
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
but this time it's a list of hashes available on the node. Use they for access to the files.
The same result will be as you visit http://your.host.org/api/files .

.. _response: http://docs.python-requests.org/en/latest/api/#requests.Response

In example::

    >>> response = metatool.core.files('http://node2.metadisk.org/')
    >>> json.loads(response.text)
    ['1d5ae562cc38e3adcf01a062207c2894fb8d055cfcf8200c3854c77eb6965645',
    '103de8978a393c6479a092ce22cf04a6dd8876039c53b66df8384f361f60163c',
    '6f9745658c158a8b61b340164c9b899f26afbc0d823f5e4d2d92872b53eda9b0',
    '6da1054eef20b8949622f2acc5a89c3243ff3b3d7aa8c2bb8fa5c04d15113c00',
    '1a8b26b9ce3983ff21d0d85c796ad75c1d2d6047ec3f082497eb1a33e8120f3e',
    '51484ac97ae37f52655160d714eb2c6ac56909aa2d170cd7812e01c35544db23']

