Welcome to MetaTool's documentation!
====================================

**metatool** is a Python package purposed for interacting with
the MetaDisk service. Package provide CLI utility ``metatool`` based on
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
   | mock_ (only for Python 2.x)

.. _btctxstore: https://pypi.python.org/pypi/btctxstore/4.6.0
.. _requests: https://pypi.python.org/pypi/requests
.. _mock: https://pypi.python.org/pypi/mock

-----------

Code Source
-----------
Visit the **MetaTool** GitHub repository - https://github.com/Storj/metatool


--------

Contents
--------

.. toctree::
   :maxdepth: 2

   core_module
   cli_module


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

