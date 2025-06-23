import datetime
from io import BytesIO

from aerofiles.igc import Writer

from freezegun import freeze_time

import pytest


@pytest.fixture()
def output():
    return BytesIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == b'line\r\n'


@pytest.fixture(params=['XXX', 'GCS', 'FIL', 'FLA'])
def manufacturer_code(request):
    return request.param


@pytest.fixture(params=['ABC', 'NG6', 'ART'])
def logger_id(request):
    return request.param


def test_logger_id(writer, manufacturer_code, logger_id):
    writer.write_logger_id(manufacturer_code, logger_id)
    assert writer.fp.getvalue() == \
        ('A%s%s\r\n' % (manufacturer_code, logger_id)).encode('utf-8')


def test_logger_id_with_extension(writer, manufacturer_code, logger_id):
    writer.write_logger_id(manufacturer_code, logger_id, 'FLIGHT:1')
    assert writer.fp.getvalue() == \
        ('A%s%sFLIGHT:1\r\n' % (manufacturer_code, logger_id)).encode('utf-8')


def test_logger_id_with_invalid_manufacturer_code(writer):
    with pytest.raises(ValueError):
        writer.write_logger_id('x_1', 'ABC')


def test_logger_id_with_invalid_logger_id(writer):
    with pytest.raises(ValueError):
        writer.write_logger_id('XXX', '12345')


def test_logger_id_without_validation(writer):
    writer.write_logger_id('a4%', '12345', validate=False)
    assert writer.fp.getvalue() == b'Aa4%12345\r\n'


def test_invalid_header_source(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_header('X', 'XXX', 'ABC')

    assert 'Invalid source: X' in str(ex)


@pytest.fixture(params=[(1996, 12, 24), (2014, 1, 31), (2032, 8, 5)])
def date(request):
    return datetime.date(*request.param)


def test_date(writer, date):
    writer.write_date(date)
    assert writer.fp.getvalue() == \
        date.strftime('HFDTE%d%m%y\r\n').encode('utf-8')


def test_invalid_date(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_date('0222')

    assert 'Invalid date: 0222' in str(ex)


@pytest.fixture(params=[20, 500, 999])
def fix_accuracy(request):
    return request.param


def test_fix_accuracy(writer, fix_accuracy):
    writer.write_fix_accuracy(fix_accuracy)
    assert writer.fp.getvalue() == \
        ('HFFXA%03d\r\n' % fix_accuracy).encode('utf-8')


def test_default_fix_accuracy(writer):
    writer.write_fix_accuracy()
    assert writer.fp.getvalue() == b'HFFXA500\r\n'


def test_invalid_fix_accuracy(writer):
    with pytest.raises(ValueError):
        writer.write_fix_accuracy(0)

    with pytest.raises(ValueError):
        writer.write_fix_accuracy(1000)


@pytest.fixture(params=[
    'Tobias Bieniek',
    'Some guy named FOO',
    'Deep Thought',
])
def pilot(request):
    return request.param


def test_pilot(writer, pilot):
    writer.write_pilot(pilot)
    assert writer.fp.getvalue() == \
        ('HFPLTPILOTINCHARGE:%s\r\n' % pilot).encode('utf-8')


def test_copilot(writer, pilot):
    writer.write_copilot(pilot)
    assert writer.fp.getvalue() == \
        ('HFCM2CREW2:%s\r\n' % pilot).encode('utf-8')


@pytest.fixture(params=['Hornet', 'JS1', 'ASW-22 BLE'])
def glider_type(request):
    return request.param


def test_glider_type(writer, glider_type):
    writer.write_glider_type(glider_type)
    assert writer.fp.getvalue() == \
        ('HFGTYGLIDERTYPE:%s\r\n' % glider_type).encode('utf-8')


@pytest.fixture(params=['D-4449', 'N116EL', '2648'])
def glider_id(request):
    return request.param


def test_glider_id(writer, glider_id):
    writer.write_glider_id(glider_id)
    assert writer.fp.getvalue() == \
        ('HFGIDGLIDERID:%s\r\n' % glider_id).encode('utf-8')


def test_gps_datum(writer):
    writer.write_gps_datum(33, 'Guam-1963')
    assert writer.fp.getvalue() == b'HFDTM033GPSDATUM:Guam-1963\r\n'


def test_default_gps_datum(writer):
    writer.write_gps_datum()
    assert writer.fp.getvalue() == b'HFDTM100GPSDATUM:WGS-1984\r\n'


@pytest.fixture(params=['6.4', 'Flarm-IGC05.09'])
def firmware_version(request):
    return request.param


def test_firmware_version(writer, firmware_version):
    writer.write_firmware_version(firmware_version)
    assert writer.fp.getvalue() == \
        ('HFRFWFIRMWAREVERSION:%s\r\n' % firmware_version).encode('utf-8')


@pytest.fixture(params=['1.2', 'Flarm-IGC06'])
def hardware_version(request):
    return request.param


def test_hardware_version(writer, hardware_version):
    writer.write_hardware_version(hardware_version)
    assert writer.fp.getvalue() == \
        ('HFRHWHARDWAREVERSION:%s\r\n' % hardware_version).encode('utf-8')


@pytest.fixture(params=[
    'Flarm-IGC',
    'FILSER,LX5000IGC-2',
    'LXNAVIGATION,LX8000F',
    'XCSOAR XCSOAR Android 6.4.3 Nov  1 2012',
])
def logger_type(request):
    return request.param


def test_logger_type(writer, logger_type):
    writer.write_logger_type(logger_type)
    assert writer.fp.getvalue() == \
        ('HFFTYFRTYPE:%s\r\n' % logger_type).encode('utf-8')


@pytest.fixture(params=[
    'uBLOX LEA-4S-2,16,max9000m',
    'JRC/CCA-450',
    'u-blox:LEA-4P,16,8191',
    'Internal GPS (Android)',
])
def gps_receiver(request):
    return request.param


def test_gps_receiver(writer, gps_receiver):
    writer.write_gps_receiver(gps_receiver)
    assert writer.fp.getvalue() == \
        ('HFGPSRECEIVER:%s\r\n' % gps_receiver).encode('utf-8')


@pytest.fixture(params=[
    'INTERSEMA,MS5534A,max10000m',
    'Intersema MS5534B,8191',
])
def pressure_sensor(request):
    return request.param


def test_pressure_sensor(writer, pressure_sensor):
    writer.write_pressure_sensor(pressure_sensor)
    assert writer.fp.getvalue() == \
        ('HFPRSPRESSALTSENSOR:%s\r\n' % pressure_sensor).encode('utf-8')


@pytest.fixture(params=['TH', '6H', '37', 'B', 'FUN'])
def competition_id(request):
    return request.param


def test_competition_id(writer, competition_id):
    writer.write_competition_id(competition_id)
    assert writer.fp.getvalue() == \
        ('HFCIDCOMPETITIONID:%s\r\n' % competition_id).encode('utf-8')


@pytest.fixture(params=['Std', 'CLUB', '15M', 'Open'])
def competition_class(request):
    return request.param


def test_competition_class(writer, competition_class):
    writer.write_competition_class(competition_class)
    assert writer.fp.getvalue() == \
        ('HFCCLCOMPETITIONCLASS:%s\r\n' % competition_class).encode('utf-8')


@pytest.fixture(params=['SFN', 'LV Aachen'])
def club(request):
    return request.param


def test_club(writer, club):
    writer.write_club(club)
    assert writer.fp.getvalue() == \
        ('HFCLBCLUB:%s\r\n' % club).encode('utf-8')


def test_headers(writer):
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
        'club': 'LV Aachen',
    })

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'AXCSTBX',
        b'HFDTE240287',
        b'HFFXA050',
        b'HFPLTPILOTINCHARGE:Tobias Bieniek',
        b'HFCM2CREW2:John Doe',
        b'HFGTYGLIDERTYPE:Duo Discus',
        b'HFGIDGLIDERID:D-KKHH',
        b'HFDTM100GPSDATUM:WGS-1984',
        b'HFRFWFIRMWAREVERSION:2.2',
        b'HFRHWHARDWAREVERSION:2',
        b'HFFTYFRTYPE:LXNAVIGATION,LX8000F',
        b'HFGPSRECEIVER:uBLOX LEA-4S-2,16,max9000m',
        b'HFPRSPRESSALTSENSOR:INTERSEMA,MS5534A,max10000m',
        b'HFCIDCOMPETITIONID:2H',
        b'HFCCLCOMPETITIONCLASS:Doubleseater',
        b'HFCLBCLUB:LV Aachen',
    ]) + b'\r\n'


def test_default_headers(writer):
    writer.write_headers({
        'manufacturer_code': 'FLA',
        'logger_id': '6NG',
        'date': datetime.date(2013, 4, 1),
        'logger_type': 'Flarm-IGC',
        'gps_receiver': 'u-blox:LEA-4P,16,8191',
    })

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'AFLA6NG',
        b'HFDTE010413',
        b'HFFXA500',
        b'HFPLTPILOTINCHARGE:',
        b'HFGTYGLIDERTYPE:',
        b'HFGIDGLIDERID:',
        b'HFDTM100GPSDATUM:WGS-1984',
        b'HFRFWFIRMWAREVERSION:',
        b'HFRHWHARDWAREVERSION:',
        b'HFFTYFRTYPE:Flarm-IGC',
        b'HFGPSRECEIVER:u-blox:LEA-4P,16,8191',
        b'HFPRSPRESSALTSENSOR:',
    ]) + b'\r\n'


def test_missing_headers(writer):
    with pytest.raises(ValueError):
        writer.write_headers({})


def test_fix_extensions(writer):
    writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])
    assert writer.fp.getvalue() == b'I033638FXA3940SIU4143ENL\r\n'


def test_empty_fix_extensions(writer):
    writer.write_fix_extensions([])
    assert writer.fp.getvalue() == b'I00\r\n'


def test_invalid_fix_extensions(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_fix_extensions(('42', 42) * 100)

    assert 'Too many extensions' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_fix_extensions([('42', 42)])

    assert 'Invalid extension: 42' in str(ex)


def test_k_record_extensions(writer):
    writer.write_k_record_extensions([('HDT', 5)])
    assert writer.fp.getvalue() == b'J010812HDT\r\n'


def test_empty_k_record_extensions(writer):
    writer.write_k_record_extensions([])
    assert writer.fp.getvalue() == b'J00\r\n'


def test_invalid_k_record_extensions(writer):
    with pytest.raises(ValueError):
        writer.write_k_record_extensions([('42', 42)])


def test_task_metadata(writer):
    writer.write_task_metadata(
        datetime.datetime(2014, 4, 13, 12, 53, 2),
        flight_date=datetime.date(2014, 4, 14),
        task_number=42,
        turnpoints=3,
        text='Some more metadata',
    )
    assert writer.fp.getvalue() == \
        b'C130414125302140414004203Some more metadata\r\n'


def test_default_task_metadata(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_task_metadata(turnpoints=1)

    assert writer.fp.getvalue() == b'C140112032134000000000101\r\n'


def test_task_metadata_with_invalid_datetime(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_task_metadata('xxx', turnpoints=2)

    assert 'Invalid declaration datetime: xxx' in str(ex)


def test_task_metadata_with_invalid_tasknumber(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_task_metadata(task_number='xxx', turnpoints=2)

    assert 'Invalid task number: xxx' in str(ex)


def test_task_metadata_with_invalid_turnpoints(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_task_metadata()

    assert 'Invalid turnpoints: None' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_task_metadata(turnpoints='xxx')

    assert 'Invalid turnpoints: xxx' in str(ex)


def test_task_point(writer):
    writer.write_task_point(
        latitude=(51 + 7.345 / 60.),
        longitude=(6 + 24.765 / 60.),
        text='Meiersberg',
    )
    assert writer.fp.getvalue() == b'C5107345N00624765EMeiersberg\r\n'


def test_task_point_with_negative_coordinates(writer):
    writer.write_task_point(
        latitude=-(12 + 32.112 / 60.),
        longitude=-(178 + .001 / 60.),
        text='TAKEOFF',
    )
    assert writer.fp.getvalue() == b'C1232112S17800001WTAKEOFF\r\n'


def test_task_point_with_area(writer):
    writer.write_task_point(
        -(12 + 32.112 / 60.),
        -(178 + .001 / 60.),
        'TURN AREA',
        distance_min=12.0,
        distance_max=32.0,
        bearing1=122.0,
        bearing2=182.0,
    )
    assert writer.fp.getvalue() == \
        b'C1232112S17800001W00120000032000122000182000TURN AREA\r\n'


def test_default_task_point(writer):
    writer.write_task_point()
    assert writer.fp.getvalue() == b'C0000000N00000000E\r\n'


def test_task_points(writer):
    writer.write_task_points([
        (None, None, 'TAKEOFF'),
        (51.40375, 6.41275, 'START'),
        (50.38210, 8.82105, 'TURN 1'),
        (50.59045, 7.03555, 'TURN 2', 0, 32.5, 0, 180),
        (51.40375, 6.41275, 'FINISH'),
        (None, None, 'LANDING'),
    ])

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'C0000000N00000000ETAKEOFF',
        b'C5124225N00624765ESTART',
        b'C5022926N00849263ETURN 1',
        b'C5035427N00702133E00000000032500000000180000TURN 2',
        b'C5124225N00624765EFINISH',
        b'C0000000N00000000ELANDING',
    ]) + b'\r\n'


def test_invalid_task_points(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_task_points([
            (None, None, None, None),
        ])

    assert 'Invalid number of task point tuple items' in str(ex)


def test_security(writer):
    writer.write_security('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert writer.fp.getvalue() == b'GABCDEFGHIJKLMNOPQRSTUVWXYZ\r\n'


def test_long_security(writer):
    writer.write_security('A' * 100)
    assert writer.fp.getvalue() == b'\r\n'.join([
        b'G' + b'A' * 75,
        b'G' + b'A' * 25,
    ]) + b'\r\n'


def test_custom_long_security(writer):
    writer.write_security('A' * 110, bytes_per_line=25)
    assert writer.fp.getvalue() == b'\r\n'.join([
        b'G' + b'A' * 25,
        b'G' + b'A' * 25,
        b'G' + b'A' * 25,
        b'G' + b'A' * 25,
        b'G' + b'A' * 10,
    ]) + b'\r\n'


def test_fix(writer):
    writer.write_fix(
        datetime.time(12, 34, 56),
        latitude=51.40375,
        longitude=6.41275,
        valid=True,
        pressure_alt=1234,
        gps_alt=1432,
    )
    assert writer.fp.getvalue() == b'B1234565124225N00624765EA0123401432\r\n'


def test_default_fix(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_fix()
    assert writer.fp.getvalue() == b'B0321340000000N00000000EV0000000000\r\n'


def test_fix_with_extensions(writer):
    writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])
    writer.write_fix(datetime.time(2, 3, 4), extensions=['023', 13, 2])

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'I033638FXA3940SIU4143ENL',
        b'B0203040000000N00000000EV000000000002313002',
    ]) + b'\r\n'


def test_fix_with_long_extensions(writer):
    writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 100)])
    writer.write_fix(datetime.time(2, 3, 4), extensions=['023', 13, 2])

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'I033638FXA3940SIU41140ENL',
        b'B0203040000000N00000000EV0000000000023130000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002',
    ]) + b'\r\n'


def test_fix_with_missing_extensions(writer):
    writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])

    with pytest.raises(ValueError) as ex:
        writer.write_fix(datetime.time(2, 3, 4))

    assert 'Invalid extensions list' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_fix(datetime.time(2, 3, 4), extensions=['023'])

    assert 'Number of extensions does not match declaration' in str(ex)


def test_fix_with_missing_extensions_declaration(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_fix(datetime.time(2, 3, 4), extensions=['023', 13, 2])

    assert 'Invalid extensions list' in str(ex)


def test_fix_with_invalid_extension(writer):
    writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])

    with pytest.raises(ValueError) as ex:
        writer.write_fix(datetime.time(2, 3, 4), extensions=['x', 13, 2])

    assert 'Extension value has wrong length' in str(ex)


def test_fix_with_invalid_time(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_fix('abcdef')

    assert 'Invalid time: abcdef' in str(ex)


def test_fix_with_invalid_latitude(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_fix(latitude=-112.34)

    assert 'Invalid latitude:' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_fix(latitude=91.2)

    assert 'Invalid latitude:' in str(ex)


def test_fix_with_invalid_longitude(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_fix(longitude=-181)

    assert 'Invalid longitude:' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_fix(longitude=215)

    assert 'Invalid longitude:' in str(ex)


def test_event(writer):
    writer.write_event(datetime.time(12, 34, 56), 'PEV')
    assert writer.fp.getvalue() == b'E123456PEV\r\n'


def test_event_with_text(writer):
    writer.write_event(datetime.time(1, 2, 3), 'PEV', 'This is a test')
    assert writer.fp.getvalue() == b'E010203PEVThis is a test\r\n'


def test_event_with_default_time(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_event('PEV')
    assert writer.fp.getvalue() == b'E032134PEV\r\n'


def test_event_with_default_time_and_text(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_event('PEV', 'Test')
    assert writer.fp.getvalue() == b'E032134PEVTest\r\n'


def test_event_with_invalid_arguments(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_event()

    assert 'Invalid number of parameters received' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_event(1, 2, 3, 4)

    assert 'Invalid number of parameters received' in str(ex)


def test_event_with_invalid_code(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_event('X')

    assert 'Invalid event code' in str(ex)


def test_satellites(writer):
    writer.write_satellites(datetime.time(12, 34, 56), [2, 52, 33, '03'])
    assert writer.fp.getvalue() == b'F12345602523303\r\n'


def test_satellites_with_default_time(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_satellites([2, 4, 99])
    assert writer.fp.getvalue() == b'F032134020499\r\n'


def test_satellites_with_invalid_id(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_satellites(['ABCDE'])

    assert 'Invalid satellite ID' in str(ex)


def test_satellites_with_invalid_arguments(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_satellites()

    assert 'Invalid number of parameters received' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_satellites(1, 2, 3)

    assert 'Invalid number of parameters received' in str(ex)


def test_k_record(writer):
    writer.write_k_record_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])
    writer.write_k_record(datetime.time(2, 3, 4), ['023', 13, 2])

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'J030810FXA1112SIU1315ENL',
        b'K02030402313002',
    ]) + b'\r\n'


def test_k_record_with_default_time(writer):
    writer.write_k_record_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])

    with freeze_time("2012-01-14 03:21:34"):
        writer.write_k_record(['023', 13, 2])

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'J030810FXA1112SIU1315ENL',
        b'K03213402313002',
    ]) + b'\r\n'


def test_k_record_with_missing_arguments(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_k_record()

    assert 'Invalid number of parameters received' in str(ex)


def test_k_record_with_missing_extensions(writer):
    writer.write_k_record_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])

    with pytest.raises(ValueError) as ex:
        writer.write_k_record(datetime.time(2, 3, 4), ['023'])

    assert 'Number of extensions does not match declaration' in str(ex)


def test_k_record_with_missing_extensions_declaration(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_k_record(datetime.time(2, 3, 4), ['023', 13, 2])

    assert 'Invalid extensions list' in str(ex)


def test_k_record_with_invalid_extension(writer):
    writer.write_k_record_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])

    with pytest.raises(ValueError) as ex:
        writer.write_k_record(datetime.time(2, 3, 4), ['x', 13, 2])

    assert 'Extension value has wrong length' in str(ex)


def test_comment(writer):
    writer.write_comment('PLT', 'This flight was my second 1000km attempt')
    assert writer.fp.getvalue() == \
        b'LPLTThis flight was my second 1000km attempt\r\n'


def test_comment_with_invalid_source(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_comment('X', 'bla')

    assert 'Invalid source' in str(ex)


def test_igc_example(writer):
    writer.write_headers({
        'manufacturer_code': 'XXX',
        'logger_id': 'ABC',
        'logger_id_extension': 'FLIGHT:1',
        'date': datetime.date(2009, 7, 16),
        'fix_accuracy': 35,
        'pilot': 'Bloggs Bill D',
        'glider_type': 'Schempp Ventus2cxa',
        'glider_id': 'ABCD-1234',
        'firmware_version': '6.4',
        'hardware_version': '3.0',
        'logger_type': 'Manufacturer, Model',
        'gps_receiver': 'MarconiCanada:Superstar,12ch, max10000m',
        'pressure_sensor': 'Sensyn, XYZ1111, max11000m',
        'competition_id': 'XYZ-78910',
        'competition_class': '15m Motor Glider',
    })

    writer.write_fix_extensions([
        ('FXA', 3),
        ('SIU', 2),
        ('ENL', 3),
    ])

    writer.write_k_record_extensions([
        ('HDT', 5),
    ])

    writer.write_task_metadata(
        datetime.datetime(2001, 7, 15, 21, 38, 41),
        datetime.datetime(2001, 7, 16),
        turnpoints=2,
        text='500K Tri',
    )

    writer.write_task_points([
        (51.18932, -1.03165, 'Lasham Clubhouse'),
        (51.16965, -1.04407, 'Lasham Start S, Start'),
        (52.15153, -2.92045, 'Sarnesfield, TP1'),
        (52.50245, -0.29353, 'Norman Cross, TP2'),
        (51.16965, -1.04407, 'Lasham Start S, Finish'),
        (51.18932, -1.03165, 'Lasham Clubhouse'),
    ])

    writer.write_satellites(datetime.time(16, 2, 40), [
        4, 6, 9, 12, 36, 24, 22, 18, 21
    ])

    writer.write_fix(
        datetime.time(16, 2, 40),
        54 + 7.121 / 60,
        -2 - 49.342 / 60,
        valid=True,
        pressure_alt=280,
        gps_alt=421,
        extensions=[205, 9, 950],
    )

    writer.write_event(datetime.time(16, 2, 45), 'PEV')

    writer.write_fix(
        datetime.time(16, 2, 45),
        51 + 7.126 / 60,
        -1 - 49.300 / 60,
        valid=True,
        pressure_alt=288,
        gps_alt=429,
        extensions=[195, 9, 20],
    )
    writer.write_fix(
        datetime.time(16, 2, 50),
        51 + 7.134 / 60,
        -1 - 49.283 / 60,
        valid=True,
        pressure_alt=290,
        gps_alt=432,
        extensions=[210, 9, 15],
    )
    writer.write_fix(
        datetime.time(16, 2, 55),
        51 + 7.140 / 60,
        -1 - 49.221 / 60,
        valid=True,
        pressure_alt=290,
        gps_alt=430,
        extensions=[200, 9, 12],
    )

    writer.write_satellites(datetime.time(16, 3, 0), [
        6, 9, 12, 36, 24, 22, 18, 21
    ])

    writer.write_fix(
        datetime.time(16, 3, 00),
        51 + 7.150 / 60,
        -1 - 49.202 / 60,
        valid=True,
        pressure_alt=291,
        gps_alt=432,
        extensions=[256, 8, 9],
    )

    writer.write_event(datetime.time(16, 3, 5), 'PEV')

    writer.write_fix(
        datetime.time(16, 3, 5),
        51 + 7.180 / 60,
        -1 - 49.185 / 60,
        valid=True,
        pressure_alt=291,
        gps_alt=435,
        extensions=[210, 8, 15],
    )
    writer.write_fix(
        datetime.time(16, 3, 10),
        51 + 7.212 / 60,
        -1 - 49.174 / 60,
        valid=True,
        pressure_alt=293,
        gps_alt=435,
        extensions=[196, 8, 24],
    )

    writer.write_k_record(datetime.time(16, 2, 48), [90])

    writer.write_fix(
        datetime.time(16, 2, 48),
        51 + 7.220 / 60,
        -1 - 49.150 / 60,
        valid=True,
        pressure_alt=494,
        gps_alt=436,
        extensions=[190, 8, 18],
    )
    writer.write_fix(
        datetime.time(16, 2, 52),
        51 + 7.330 / 60,
        -1 - 49.127 / 60,
        valid=True,
        pressure_alt=496,
        gps_alt=439,
        extensions=[195, 8, 15],
    )

    writer.write_comment('XXX', 'RURITANIAN STANDARD NATIONALS DAY 1')
    writer.write_comment('XXX', 'FLIGHT TIME: 4:14:25, TASK SPEED:58.48KTS')

    writer.write_security(
        'REJNGJERJKNJKRE31895478537H43982FJN9248F942389T433T'
        'JNJK2489IERGNV3089IVJE9GO398535J3894N358954983O0934'
        'SKTO5427FGTNUT5621WKTC6714FT8957FGMKJ134527FGTR6751'
        'K2489IERGNV3089IVJE39GO398535J3894N358954983FTGY546'
        '12560DJUWT28719GTAOL5628FGWNIST78154INWTOLP7815FITN',
        bytes_per_line=51
    )

    assert writer.fp.getvalue() == b'\r\n'.join([
        b'AXXXABCFLIGHT:1',
        b'HFDTE160709',
        b'HFFXA035',
        b'HFPLTPILOTINCHARGE:Bloggs Bill D',
        b'HFGTYGLIDERTYPE:Schempp Ventus2cxa',
        b'HFGIDGLIDERID:ABCD-1234',
        b'HFDTM100GPSDATUM:WGS-1984',
        b'HFRFWFIRMWAREVERSION:6.4',
        b'HFRHWHARDWAREVERSION:3.0',
        b'HFFTYFRTYPE:Manufacturer, Model',
        b'HFGPSRECEIVER:MarconiCanada:Superstar,12ch, max10000m',
        b'HFPRSPRESSALTSENSOR:Sensyn, XYZ1111, max11000m',
        b'HFCIDCOMPETITIONID:XYZ-78910',
        b'HFCCLCOMPETITIONCLASS:15m Motor Glider',
        b'I033638FXA3940SIU4143ENL',
        b'J010812HDT',
        b'C150701213841160701000102500K Tri',
        b'C5111359N00101899WLasham Clubhouse',
        b'C5110179N00102644WLasham Start S, Start',
        b'C5209092N00255227WSarnesfield, TP1',
        b'C5230147N00017612WNorman Cross, TP2',
        b'C5110179N00102644WLasham Start S, Finish',
        b'C5111359N00101899WLasham Clubhouse',
        b'F160240040609123624221821',
        b'B1602405407121N00249342WA002800042120509950',
        b'E160245PEV',
        b'B1602455107126N00149300WA002880042919509020',
        b'B1602505107134N00149283WA002900043221009015',
        b'B1602555107140N00149221WA002900043020009012',
        b'F1603000609123624221821',
        b'B1603005107150N00149202WA002910043225608009',
        b'E160305PEV',
        b'B1603055107180N00149185WA002910043521008015',
        b'B1603105107212N00149174WA002930043519608024',
        b'K16024800090',
        b'B1602485107220N00149150WA004940043619008018',
        b'B1602525107330N00149127WA004960043919508015',
        b'LXXXRURITANIAN STANDARD NATIONALS DAY 1',
        b'LXXXFLIGHT TIME: 4:14:25, TASK SPEED:58.48KTS',
        b'GREJNGJERJKNJKRE31895478537H43982FJN9248F942389T433T',
        b'GJNJK2489IERGNV3089IVJE9GO398535J3894N358954983O0934',
        b'GSKTO5427FGTNUT5621WKTC6714FT8957FGMKJ134527FGTR6751',
        b'GK2489IERGNV3089IVJE39GO398535J3894N358954983FTGY546',
        b'G12560DJUWT28719GTAOL5628FGWNIST78154INWTOLP7815FITN',
    ]) + b'\r\n'
