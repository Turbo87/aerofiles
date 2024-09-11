Changelog
=========

Here you can see the full list of changes between each aerofiles release.

aerofiles vXXX, 2024-XX-YYYY
----------------------------
- igc/reader: fix for HFTZN to handle timezone that is not integer
- igc/reader: add "datetime" and "datetime_local" to fix_records to
              deal with UTC and local time correctly. Please read "How
              to read an IGC file" for a detailed explanation.

aerofiles v1.3.1, 2024-08-12
----------------------------
- messed up v1.3.0 deployment. Redeploy as v1.3.1 without any changes.

aerofiles v1.3.0, 2024-08-12
----------------------------
- openair/writer: first implementation of type "airspace". Others are missing
- openair: implement extended openair format
- openair: various smaller bug fixes

aerofiles v1.2.1
----------------
- seeyou/writer: fix in writer to use ";" as delimiter for pics


aerofiles v1.2.0
----------------
- seeyou: handle newer file formats including rwwidth, userdata and pics.


aerofiles v1.1.1
----------------

- v1.1.0 failed to be published because of wrong GitHub action. Fixed


aerofiles v1.1.0
----------------

- IGC/writer: added long_option "RECEIVER" to be compliant with newest spec
- IGC/reader: allow all H-records to be in short or long format
- OpenAir/reader: Added "lineno" to all elements to reference source line


aerofiles v1.0.0
----------------

- fix decode_date bug in igc.reader
- remove python2.6 and python3.3 support


aerofiles v0.4.1
----------------

- fix extensions in IGC file fix record
- remove igc line limit


aerofiles v0.4
--------------

- IGC file reader
- Expanded SeeYou reader with task reading


aerofiles v0.3
--------------

- OpenAir airspace file reader
- Fixed encoding issues in SeeYou/XCSoar file writers


aerofiles v0.2
--------------

- SeeYou CUP file writer
- XCSoar task file writer
- Flarm configuration file writer


aerofiles v0.1.1
----------------

- Fixed missing README.rst in source distribution


aerofiles v0.1
--------------

First public preview release

- SeeYou CUP file reader
- WELT2000 file reader
- IGC file writer
