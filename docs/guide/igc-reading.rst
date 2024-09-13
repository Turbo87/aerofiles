How to read an IGC file
=======================

aerofiles has the :class:`aerofiles.igc.Reader` class for reading IGC files::

    with open('track.igc', 'r') as f:
        igc = Reader().read(f)

The result is returned in ``igc`` which is a dict containing the IGC
file content. The most important keys are ``header`` and
``fix_records``. The other keys are mainly self explanatory. Every
value consists of two elements. The first is an array of error
messages for this key and the second one is a list of the
elements. For example ``igc["fix_records"][0]`` is a list of possible
errors (normally empty) and ``igc["fix_records"][1]`` is a list of the
fixes. See below for more details.

The constructor of :class:`aerofiles.igc.Reader` takes an optional
argument ``skip_duplicates`` which defaults to ``False``. If you set
it to true, then all GPS fixes which contain the same time as a
previous one will be skipped and not returned as a result.


Headers
-------

The header consists of all header elements of the IGC file. Here is an
example of ``igc["header"][1]``::

    {'competition_class': '15m Motor Glider',
     'competition_id': 'XYZ-78910',
     'copilot': 'Smith-Barry John A',
     'firmware_revision': '6.4',
     'fix_accuracy': 35,
     'glider_model': 'Schleicher ASH-25',
     'glider_registration': 'ABCD-1234',
     'gps_channels': 12,
     'gps_datum': 'WGS-1984',
     'gps_manufacturer': 'MarconiCanada',
     'gps_max_alt': {'unit': 'm', 'value': 10000},
     'gps_model': 'Superstar',
     'hardware_revision': '3.0',
     'logger_manufacturer': 'Manufacturer',
     'logger_model': 'Model',
     'pilot': 'Bloggs Bill D',
     'pressure_sensor_manufacturer': 'Sensyn',
     'pressure_sensor_max_alt': {'unit': 'm', 'value': 11000},
     'pressure_sensor_model': 'XYZ1111',
     'time_zone_offset': 3.0,
     'utc_date': datetime.date(2001, 7, 16)}],
    }


GPS Fixes
---------

The following example IGC file is read. For simplicity it is very
short and misses some mandatory fields::
  
    HFDTE160701
    HFTZNTIMEZONE:-6.00
    B1602405407121N00249342WA002800042120509950


The GPS fixes are found in ``igc["fix_records"][1]`` and are a list of
dicts for every fix::

    [{'ENL': 950,
      'FXA': 205,
      'SIU': 9,
      'datetime': datetime.datetime(2001, 7, 16, 16, 2, 40, tzinfo=<aerofiles.util.timezone.TimeZoneFix object at 0x7fd061c02390>),
      'datetime_local': datetime.datetime(2001, 7, 16, 10, 2, 40, tzinfo=<aerofiles.util.timezone.TimeZoneFix object at 0x7fd061c02120>),
      'gps_alt': 421,
      'lat': 54.11868333333334,
      'lon': -2.8223666666666665,
      'pressure_alt': 280,
      'time': datetime.time(16, 2, 40),
      'validity': 'A'}]

Most values should be self explanatory.

An important aspect are dates, times and timezones. IGC files store
all times in UTC. This means that ``"time"`` is the time of the fix as
found in the IGC and it is always in UTC [1]_. The times of the fixes
are always increasing as the recording takes part. Normally a flight
is recorded during daylight and so you may assume, that there is no
roll over taking part. However, as IGC files are recorded in UTC this
might not be true. If you record a flight in timezone "-06:00" and you
start your flight at "17:59", then UTC time is already "23:59". The
``B`` record one minute later will be at "00:00", so it is less than
the previous time. You have to handle this yourself, if you use
``"time"``.

A solution for this problem is ``"datetime"``, which is available since
aerofiles v1.4.0. It is a timezone aware instance of
``datetime.datetime`` with a timezone of UTC. The date part is taking
from the header field ``HFDTE`` and the time is taken from the ``B``
record. It will be always incrementing, as it also contains a date
(which may increase as well in the above example).

If your IGC file contains a ``HFTZN`` header telling the timezone
where the recording took place, then you will also find
``"datetime_local"``. It is the datetime of the fix converted to local
time with the given timezone from the header. This is probably the
datetime, you are looking for. Please note, that the IGC file
specification does not handle a change of timezone during flight. So
if you cross borders to a different timezone or daylight savings
change occur during flight, then there is no way to record this change
in an IGC file. The times of the fixes will then be wrong.


.. [1] The ``time`` object is an instance of ``datetime.time`` and it
       is "naive". This means, it has no timezone awareness. It would
       have been better to make it aware with ``datetime.UTC``, but
       this has not been done on the first releases of aerofiles. To
       keep compatibility, we kept it naive. So you find here the
       exact UTC time as found in the IGC file without any timezone
       attached.

