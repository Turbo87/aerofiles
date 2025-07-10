|aerofiles|
===========

**airspace, waypoint, task, tracklog readers and writers for aviation**

This is a python library to read and write many important file formats
for aviation. It is compatible with python 3.0 (and newer) and 2.6
(except AIXM which needs python 3.7). Please read the documentation
under https://aerofiles.readthedocs.io for further information.

.. image:: ../../actions/workflows/ci.yml/badge.svg
   :target: ../../actions/workflows/ci.yml
   :alt: Build Status

Features
--------

-  `AIXM <http://aixm.aero/>`_ read AIXM 5.1.1 airspaces (``aerofiles.aixm``)

   -  use [aixm-to-openair.py](aerofiles/aixm/aixm-to-openair.py) to convert AIXM into openair

-  `Flarm <http://flarm.com/>`_ configuration file writer
   (``aerofiles.flarmcfg``)
-  `IGC <https://www.fai.org/commission/igc>`_ file reader and writer (``aerofiles.igc``)
-  `OpenAir <https://github.com/naviter/seeyou_file_formats/blob/main/OpenAir_File_Format_Support.md>`_ file
   reader and writer (``aerofiles.openair``)
-  `SeeYou <http://www.naviter.com/products/seeyou/>`_ CUP file reader and
   writer (``aerofiles.seeyou``)
-  `WELT2000 <http://www.segelflug.de/vereine/welt2000/>`_ file reader
   (``aerofiles.welt2000``)
-  `XCSoar <http://www.xcsoar.org>`_ task file writer (``aerofiles.xcsoar``)

Development Environment
-----------------------

If you want to work on aerofiles you should install the necessary dependencies
using pip, preferably in a virtual environment::

    $ python -m venv .env
    $ source .env/bin/activate
    $ pip install -r requirements-dev.txt

You can run the testsuite with::

    $ make test

If you close the current shell, the virtual python environment will
also be deactivated. To continue working in the environment and using
the installed requirements, you must use this again::
  
    $ source .env/bin/activate

Building Docs
-------------

Make sure that you have checked out git submodules::

    $ git submodule update --init

Then build docs using Sphinx and Make::

   $ make doc

The HTML output can be found in the `docs/_build/html` directory.

License
-------

This code is published under the MIT license. See the
`LICENSE <https://github.com/Turbo87/aerofiles/blob/master/LICENSE>`__ file
for the full text.

How to release
--------------

Make sure, that all succeed::

 $ make lint

(and use `make lint-fix` for automatic fixing)::

 $ make vermin
 $ make test
 $ make doc-test

Ensure CHANGELOG.rst is up to date including the (next) version
number. Also check, that (next) version number is included in
setup.py.

Use browser with https://github.com/Turbo87/aerofiles/releases and
"Draft a new release". Use "Choose a tag" to create a new tag
following the structure "v1.2.1". The release title should be
"aerofiles v1.2.1". Use text from CHANGELOG.rst to describe this
release.

Finally use "Set as the latest release" and publish release.

Then go to https://readthedocs.org/projects/aerofiles/ and hit
"Build-Version" to update the documentation from github.com.

.. |aerofiles| image:: https://github.com/Turbo87/aerofiles/raw/master/img/logo.png
    :alt: aerofiles
