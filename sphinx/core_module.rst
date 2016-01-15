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

All API functions are placed in the ``metatool.core`` module which is described on the **MetaTool API specification**,
so here we'll look on their use.

To start using the MetaTool API you should get the source code from the https://github.com/Storj/metatool.git and
either install the package with the ``python setup.py install`` command or make sure that the directory nested the ``metatool`` package
is present at your ``sys.path``.

:Note: The ``metatool`` python package is not the same as root repository directory. The ``metatool`` package is the
    **metatool** subdirectory of this repository.

Let's try to use it just installed required packages - clone the repo, open it, check the requirements and try to import package::

    $ git clone https://github.com/Storj/metatool.git
    Cloning into 'metatool'...
    remote: Counting objects: 504, done.
    remote: Total 504 (delta 0), reused 0 (delta 0), pack-reused 504
    Receiving objects: 100% (504/504), 950.65 KiB | 770.00 KiB/s, done.
    Resolving deltas: 100% (279/279), done.
    Checking connectivity... done.
    $
    $ cd metatool
    $ pip install -r metatool/requirements.txt
    Ignoring mock: markers "python_version == '2.7'" don't match your environment
    Collecting btctxstore (from -r metatool/requirements.txt (line 2))
    Collecting requests (from -r metatool/requirements.txt (line 3))
      Using cached requests-2.9.1-py2.py3-none-any.whl
    Collecting future>=0.15.2 (from btctxstore->-r metatool/requirements.txt (line 2))
    Collecting pycoin>=0.52 (from btctxstore->-r metatool/requirements.txt (line 2))
    Collecting six>=1.10.0 (from btctxstore->-r metatool/requirements.txt (line 2))
      Using cached six-1.10.0-py2.py3-none-any.whl
    Collecting ecdsa>=0.13 (from btctxstore->-r metatool/requirements.txt (line 2))
      Using cached ecdsa-0.13-py2.py3-none-any.whl
    Installing collected packages: future, pycoin, six, ecdsa, btctxstore, requests
    Successfully installed btctxstore-4.6.1 ecdsa-0.13 future-0.15.2 pycoin-0.62 requests-2.9.1 six-1.10.0
    $
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

-------------------

