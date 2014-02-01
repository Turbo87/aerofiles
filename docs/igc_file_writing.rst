How to write an IGC file
========================

aerofiles has the :class:`aerofiles.igc.Writer` class for writing IGC files.
The first thing you need to do is instantiate it by passing an file-like object
into its constructor::

    with open('sample.igc', 'w') as fp:
        writer = aerofiles.igc.Writer(fp)

After that you can use the ``writer`` object to write the necessary file
headers::

    writer.write_headers({
        'manufacturer_code': 'XCS',
        'logger_id': 'TBX',
        'date': datetime.date(1987, 2, 24),
        'fix_accuracy': 50,
        'pilot': 'Tobias Bieniek',
        'copilot': 'John Doe',
        'glider_type': 'Duo Discus',
        'glider_id': 'D-KKHH',
        'firmware_version': '2.2',
        'hardware_version': '2',
        'logger_type': 'LXNAVIGATION,LX8000F',
        'gps_receiver': 'uBLOX LEA-4S-2,16,max9000m',
        'pressure_sensor': 'INTERSEMA,MS5534A,max10000m',
        'competition_id': '2H',
        'competition_class': 'Doubleseater',
    })

Note that the :meth:`~aerofiles.igc.Writer.write_headers` method will take care
of writing the headers in the right order and it will alert you if you failed
to pass a mandatory header. Those mandatory headers that are allowed to be
blank will be written without value if you don't specify any values.

The result of the call above is the following lines being written to the
``sample.igc`` file::

    AXCSTBX
    HFDTE870224
    HFFXA050
    HFPLTPILOTINCHARGE:Tobias Bieniek
    HFCM2CREW2:John Doe
    HFGTYGLIDERTYPE:Duo Discus
    HFGIDGLIDERID:D-KKHH
    HFDTM100GPSDATUM:WGS-1984
    HFRFWFIRMWAREVERSION:2.2
    HFRHWHARDWAREVERSION:2
    HFFTYFRTYPE:LXNAVIGATION,LX8000F
    HFGPSuBLOX LEA-4S-2,16,max9000m
    HFPRSPRESSALTSENSOR:INTERSEMA,MS5534A,max10000m
    HFCIDCOMPETITIONID:2H
    HFCCLCOMPETITIONCLASS:Doubleseater
