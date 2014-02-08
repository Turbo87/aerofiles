|aerofiles|
===========

**waypoint, task and tracklog file readers and writers for aviators**

.. image:: https://travis-ci.org/Turbo87/aerofiles.png?branch=master
   :target: https://travis-ci.org/Turbo87/aerofiles
   :alt: Build Status

Features
--------

-  SeeYou CUP file reader (``aerofiles.seeyou``)
-  WELT2000 file reader (``aerofiles.welt2000``)
-  IGC file writer (``aerofiles.igc``)

Development Environment
-----------------------

If you want to work on aerofiles you should install the necessary dependencies
using::

    $ pip install -r requirements-dev.txt

You can run the testsuite with::

    $ py.test

To run the whole testsuite you need to download some processable data like
this::

    $ ./download_test_data.sh

License
-------

This code is published under the MIT license. See the
`LICENSE <https://github.com/Turbo87/aerofiles/blob/master/LICENSE>`__ file
for the full text.


.. |aerofiles| image:: https://github.com/Turbo87/aerofiles/raw/master/img/logo.png
    :alt: aerofiles
