"""
**metatool** is a Python package purposed for interacting with
the MetaDisk service. Package provide CLI utility ``metatool`` based on the
MetaTool API. It developed accordingly to actions, that you can perform
with the MetaDisk service through the "curl" terminal command, described
at the http://node2.metadisk.org/ page, but have some future, like walking
through several **Nodes** looking for a file, or generating GET HTTP request
string to download file through browser for example.
"""

from . import core, cli