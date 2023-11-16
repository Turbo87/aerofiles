|aerofiles|
===========

**waypoint, task, tracklog readers and writers for aviation**

This is a python library to read and write many important file formats
for aviation. It is compatible with python 3.0 (and newer) and
2.6. Please read the documentation under
https://aerofiles.readthedocs.io for further information.

.. image:: ../../actions/workflows/ci.yml/badge.svg
   :target: ../../actions/workflows/ci.yml
   :alt: Build Status

Features
--------

-  `Flarm <http://flarm.com/>`_ configuration file writer
   (``aerofiles.flarmcfg``)
-  `IGC <https://www.fai.org/commission/igc>`_ file reader and writer (``aerofiles.igc``)
-  `OpenAir <http://www.winpilot.com/UsersGuide/UserAirspace.asp>`_ file
   reader (``aerofiles.openair``)
-  `SeeYou <http://www.naviter.com/products/seeyou/>`_ CUP file reader and
   writer (``aerofiles.seeyou``)
-  `WELT2000 <http://www.segelflug.de/vereine/welt2000/>`_ file reader
   (``aerofiles.welt2000``)
-  `XCSoar <http://www.xcsoar.org>`_ task file writer (``aerofiles.xcsoar``)

Development Environment
-----------------------

If you want to work on aerofiles you should install the necessary dependencies
using::

    $ pip install -r requirements-dev.txt

You can run the testsuite with::

    $ make test

Building Docs
-------------

Make sure that you have checked out git submodules::

    $ git submodule update --init

Then build docs using Sphinx and Make::

   $ cd docs
   $ make html

The HTML output can be found in the `_build/html` directory.

License
-------

This code is published under the MIT license. See the
`LICENSE <https://github.com/Turbo87/aerofiles/blob/master/LICENSE>`__ file
for the full text.


.. |aerofiles| image:: https://github.com/Turbo87/aerofiles/raw/master/img/logo.png
    :alt: aerofiles
