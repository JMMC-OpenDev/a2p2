a2p2 |A2P2Badge| 
================

**Move your Aspro2 observation details to an observatory proposal database**

Description
-----------

Prepare your observations within Aspro2_ and run a2p2_ to submit your OB.

You will need an account to perform operation on ESO database through P2_.


Installation
------------

The package is uploaded to `PyPI`_, so you can install the package using pip:

    ``pip install a2p2``

You can also build and install from sources:

    ``git clone https://github.com/JMMC-OpenDev/a2p2.git``

    ``cd a2p2``

    ``pip install .``

Usage
-----

**a2p2 [-h] [-f] [-u USERNAME] [-v]**


optional arguments:
 -h, --help                        show this help message and exit
 -f, --fakeapi                     fake API to avoid remote connection (dev. only).
 -u USERNAME, --username USERNAME  use another user login in history's comments.
 -v, --verbose                     Verbose

A GUI is run if your python installation supports tkinter or gtk, else a text UI will run. 

Once Aspro2_ is running and a2p2_ is connected to an OB submission service (using P2API_) :
 * select your target 
 * enter the Aspro2'menu ``interop`` / ``Send Obs. Block(s)`` 

After few seconds, you shoud get a report of your new submission.

License
-------
A2P2 is released under GPL license. Please have a look in the LICENSE file for any detail and feel free to fill issues.

Interaction diagram
-------------------
|flowchart|

.. |flowchart| image:: https://raw.githubusercontent.com/JMMC-OpenDev/a2p2/master/doc/A2P2_in_3steps.png
   :alt: A2P2 interaction diagram
   :target: https://raw.githubusercontent.com/JMMC-OpenDev/a2p2/master/doc/A2P2_in_3steps.png
.. |A2P2Badge| image:: https://travis-ci.org/JMMC-OpenDev/a2p2.svg?branch=master :alt: A2P2 Badge on master branch
   :target: https://travis-ci.org/JMMC-OpenDev/a2p2
.. _PyPI:   https://pypi.python.org
.. _P2:     https://www.eso.org/sci/observing/phase2/p2intro.html
.. _P2API:  https://www.eso.org/copdemo/apidoc/
.. _Aspro2: http://www.jmmc.fr/aspro2
.. _a2p2:   http://www.jmmc.fr/a2p2
