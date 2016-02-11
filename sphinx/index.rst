Welcome to MetaTool's documentation!
====================================


.. image:: https://travis-ci.org/Storj/metatool.svg?branch=master
    :target: https://travis-ci.org/Storj/metatool
.. image:: https://coveralls.io/repos/github/Storj/metatool/badge.svg?branch=master
    :target: https://coveralls.io/github/Storj/metatool?branch=master
.. image:: https://img.shields.io/badge/license-AGPL%20License-blue.svg
    :target: https://github.com/Storj/metatool/blob/master/LICENSE

**metatool** is a Python package purposed for interacting with
the MetaDisk service. Package provide CLI utility ``metatool`` based on the
MetaTool API. It developed accordingly to actions that you can perform
with the MetaDisk service through the "curl" terminal command, described
at the http://node2.metadisk.org/ page, but have some future, like walking
through several **Nodes** looking for a file, or generating GET HTTP request
string to download file through browser for example.

------------

Requirements
------------

**MetaTool** tested on next **Python** versions:

   * Python 2.7
   * Python 3.3
   * Python 3.4
   * Python 3.5

and require side packages:

   | btctxstore_
   | requests_
   | file_encryptor_
   | mock_ (only for Python 2.x)

.. _btctxstore: https://pypi.python.org/pypi/btctxstore/4.6.0
.. _requests: https://pypi.python.org/pypi/requests
.. _mock: https://pypi.python.org/pypi/mock
.. _file_encryptor: https://pypi.python.org/pypi/file_encryptor/0.2.9

-----------

Code Source
-----------
Visit the **MetaTool** GitHub repository - https://github.com/Storj/metatool


--------

Contents
--------

.. toctree::
   :maxdepth: 2

   package_reference
   core_module
   cli_module


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

