import pytest
from freezegun import freeze_time

import datetime

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from aerofiles.igc import Writer


@pytest.fixture()
def output():
    return StringIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == 'line\r\n'


@pytest.fixture(params=['XXX', 'GCS', 'FIL', 'FLA'])
def manufacturer_code(request):
    return request.param


@pytest.fixture(params=['ABC', 'NG6', 'ART'])
def logger_id(request):
    return request.param


def test_logger_id(writer, manufacturer_code, logger_id):
    writer.write_logger_id(manufacturer_code, logger_id)
    assert writer.fp.getvalue() == \
        'A%s%s\r\n' % (manufacturer_code, logger_id)


def test_logger_id_with_extension(writer, manufacturer_code, logger_id):
    writer.write_logger_id(manufacturer_code, logger_id, 'FLIGHT:1')
    assert writer.fp.getvalue() == \
        'A%s%sFLIGHT:1\r\n' % (manufacturer_code, logger_id)


def test_logger_id_with_invalid_manufacturer_code(writer):
    with pytest.raises(ValueError):
        writer.write_logger_id('x_1', 'ABC')


def test_logger_id_with_invalid_logger_id(writer):
    with pytest.raises(ValueError):
        writer.write_logger_id('XXX', '12345')


def test_logger_id_without_validation(writer):
    writer.write_logger_id('a4%', '12345', validate=False)
    assert writer.fp.getvalue() == 'Aa4%12345\r\n'


def test_invalid_header_source(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_header('X', 'XXX', 'ABC')

    assert 'Invalid source: X' in str(ex)


@pytest.fixture(params=[(1996, 12, 24), (2014, 1, 31), (2032, 8, 5)])
def date(request):
    return datetime.date(*request.param)


def test_date(writer, date):
    writer.write_date(date)
    assert writer.fp.getvalue() == date.strftime('HFDTE%d%m%y\r\n')


def test_invalid_date(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_date('0222')

    assert 'Invalid date: 0222' in str(ex)


@pytest.fixture(params=[20, 500, 999])
def fix_accuracy(request):
    return request.param


def test_fix_accuracy(writer, fix_accuracy):
    writer.write_fix_accuracy(fix_accuracy)
    assert writer.fp.getvalue() == 'HFFXA%03d\r\n' % fix_accuracy


def test_default_fix_accuracy(writer):
    writer.write_fix_accuracy()
    assert writer.fp.getvalue() == 'HFFXA500\r\n'


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
    assert writer.fp.getvalue() == 'HFPLTPILOTINCHARGE:%s\r\n' % pilot


def test_copilot(writer, pilot):
    writer.write_copilot(pilot)
    assert writer.fp.getvalue() == 'HFCM2CREW2:%s\r\n' % pilot


@pytest.fixture(params=['Hornet', 'JS1', 'ASW-22 BLE'])
def glider_type(request):
    return request.param


def test_glider_type(writer, glider_type):
    writer.write_glider_type(glider_type)
    assert writer.fp.getvalue() == 'HFGTYGLIDERTYPE:%s\r\n' % glider_type


@pytest.fixture(params=['D-4449', 'N116EL', '2648'])
def glider_id(request):
    return request.param


def test_glider_id(writer, glider_id):
    writer.write_glider_id(glider_id)
    assert writer.fp.getvalue() == 'HFGIDGLIDERID:%s\r\n' % glider_id


def test_gps_datum(writer):
    writer.write_gps_datum(33, 'Guam-1963')
    assert writer.fp.getvalue() == 'HFDTM033GPSDATUM:Guam-1963\r\n'


def test_default_gps_datum(writer):
    writer.write_gps_datum()
    assert writer.fp.getvalue() == 'HFDTM100GPSDATUM:WGS-1984\r\n'


@pytest.fixture(params=['6.4', 'Flarm-IGC05.09'])
def firmware_version(request):
    return request.param


def test_firmware_version(writer, firmware_version):
    writer.write_firmware_version(firmware_version)
    assert writer.fp.getvalue() == \
        'HFRFWFIRMWAREVERSION:%s\r\n' % firmware_version


@pytest.fixture(params=['1.2', 'Flarm-IGC06'])
def hardware_version(request):
    return request.param


def test_hardware_version(writer, hardware_version):
    writer.write_hardware_version(hardware_version)
    assert writer.fp.getvalue() == \
        'HFRHWHARDWAREVERSION:%s\r\n' % hardware_version


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
    assert writer.fp.getvalue() == 'HFFTYFRTYPE:%s\r\n' % logger_type


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
    assert writer.fp.getvalue() == 'HFGPS%s\r\n' % gps_receiver


@pytest.fixture(params=[
    'INTERSEMA,MS5534A,max10000m',
    'Intersema MS5534B,8191',
])
def pressure_sensor(request):
    return request.param


def test_pressure_sensor(writer, pressure_sensor):
    writer.write_pressure_sensor(pressure_sensor)
    assert writer.fp.getvalue() == \
        'HFPRSPRESSALTSENSOR:%s\r\n' % pressure_sensor


@pytest.fixture(params=['TH', '6H', '37', 'B', 'FUN'])
def competition_id(request):
    return request.param


def test_competition_id(writer, competition_id):
    writer.write_competition_id(competition_id)
    assert writer.fp.getvalue() == \
        'HFCIDCOMPETITIONID:%s\r\n' % competition_id


@pytest.fixture(params=['Std', 'CLUB', '15M', 'Open'])
def competition_class(request):
    return request.param


def test_competition_class(writer, competition_class):
    writer.write_competition_class(competition_class)
    assert writer.fp.getvalue() == \
        'HFCCLCOMPETITIONCLASS:%s\r\n' % competition_class


@pytest.fixture(params=['SFN', 'LV Aachen'])
def club(request):
    return request.param


def test_club(writer, club):
    writer.write_club(club)
    assert writer.fp.getvalue() == \
        'HFCLBCLUB:%s\r\n' % club


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

    assert writer.fp.getvalue() == '\r\n'.join([
        'AXCSTBX',
        'HFDTE240287',
        'HFFXA050',
        'HFPLTPILOTINCHARGE:Tobias Bieniek',
        'HFCM2CREW2:John Doe',
        'HFGTYGLIDERTYPE:Duo Discus',
        'HFGIDGLIDERID:D-KKHH',
        'HFDTM100GPSDATUM:WGS-1984',
        'HFRFWFIRMWAREVERSION:2.2',
        'HFRHWHARDWAREVERSION:2',
        'HFFTYFRTYPE:LXNAVIGATION,LX8000F',
        'HFGPSuBLOX LEA-4S-2,16,max9000m',
        'HFPRSPRESSALTSENSOR:INTERSEMA,MS5534A,max10000m',
        'HFCIDCOMPETITIONID:2H',
        'HFCCLCOMPETITIONCLASS:Doubleseater',
        'HFCLBCLUB:LV Aachen',
    ]) + '\r\n'


def test_default_headers(writer):
    writer.write_headers({
        'manufacturer_code': 'FLA',
        'logger_id': '6NG',
        'date': datetime.date(2013, 4, 1),
        'logger_type': 'Flarm-IGC',
        'gps_receiver': 'u-blox:LEA-4P,16,8191',
    })

    assert writer.fp.getvalue() == '\r\n'.join([
        'AFLA6NG',
        'HFDTE010413',
        'HFFXA500',
        'HFPLTPILOTINCHARGE:',
        'HFGTYGLIDERTYPE:',
        'HFGIDGLIDERID:',
        'HFDTM100GPSDATUM:WGS-1984',
        'HFRFWFIRMWAREVERSION:',
        'HFRHWHARDWAREVERSION:',
        'HFFTYFRTYPE:Flarm-IGC',
        'HFGPSu-blox:LEA-4P,16,8191',
        'HFPRSPRESSALTSENSOR:',
    ]) + '\r\n'


def test_missing_headers(writer):
    with pytest.raises(ValueError):
        writer.write_headers({})


def test_fix_extensions(writer):
    writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])
    assert writer.fp.getvalue() == 'I033638FXA3940SIU4143ENL\r\n'


def test_empty_fix_extensions(writer):
    writer.write_fix_extensions([])
    assert writer.fp.getvalue() == 'I00\r\n'


def test_invalid_fix_extensions(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_fix_extensions(('42', 42) * 100)

    assert 'Too many extensions' in str(ex)

    with pytest.raises(ValueError) as ex:
        writer.write_fix_extensions([('42', 42)])

    assert 'Invalid extension: 42' in str(ex)


def test_k_record_extensions(writer):
    writer.write_k_record_extensions([('HDT', 5)])
    assert writer.fp.getvalue() == 'J010812HDT\r\n'


def test_empty_k_record_extensions(writer):
    writer.write_k_record_extensions([])
    assert writer.fp.getvalue() == 'J00\r\n'


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
        'C130414125302140414004203Some more metadata\r\n'


def test_default_task_metadata(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_task_metadata(turnpoints=1)

    assert writer.fp.getvalue() == 'C140112032134000000000101\r\n'


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
    assert writer.fp.getvalue() == 'C5107345N00624765EMeiersberg\r\n'


def test_task_point_with_negative_coordinates(writer):
    writer.write_task_point(
        latitude=-(12 + 32.112 / 60.),
        longitude=-(178 + .001 / 60.),
        text='TAKEOFF',
    )
    assert writer.fp.getvalue() == 'C1232112S17800001WTAKEOFF\r\n'


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
        'C1232112S17800001W00120000032000122000182000TURN AREA\r\n'


def test_default_task_point(writer):
    writer.write_task_point()
    assert writer.fp.getvalue() == 'C0000000N00000000E\r\n'


def test_task_points(writer):
    writer.write_task_points([
        (None, None, 'TAKEOFF'),
        (51.40375, 6.41275, 'START'),
        (50.38210, 8.82105, 'TURN 1'),
        (50.59045, 7.03555, 'TURN 2', 0, 32.5, 0, 180),
        (51.40375, 6.41275, 'FINISH'),
        (None, None, 'LANDING'),
    ])

    assert writer.fp.getvalue() == '\r\n'.join([
        'C0000000N00000000ETAKEOFF',
        'C5124225N00624765ESTART',
        'C5022926N00849263ETURN 1',
        'C5035427N00702133E00000000032500000000180000TURN 2',
        'C5124225N00624765EFINISH',
        'C0000000N00000000ELANDING',
    ]) + '\r\n'


def test_invalid_task_points(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_task_points([
            (None, None, None, None),
        ])

    assert 'Invalid number of task point tuple items' in str(ex)


def test_security(writer):
    writer.write_security('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    assert writer.fp.getvalue() == 'GABCDEFGHIJKLMNOPQRSTUVWXYZ\r\n'


def test_long_security(writer):
    writer.write_security('A' * 100)
    assert writer.fp.getvalue() == '\r\n'.join([
        'G' + 'A' * 75,
        'G' + 'A' * 25,
    ]) + '\r\n'


def test_custom_long_security(writer):
    writer.write_security('A' * 110, bytes_per_line=25)
    assert writer.fp.getvalue() == '\r\n'.join([
        'G' + 'A' * 25,
        'G' + 'A' * 25,
        'G' + 'A' * 25,
        'G' + 'A' * 25,
        'G' + 'A' * 10,
    ]) + '\r\n'


def test_fix(writer):
    writer.write_fix(
        datetime.time(12, 34, 56),
        latitude=51.40375,
        longitude=6.41275,
        valid=True,
        pressure_alt=1234,
        gps_alt=1432,
    )
    assert writer.fp.getvalue() == 'B1234565124225N00624765EA0123401432\r\n'


def test_default_fix(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_fix()
    assert writer.fp.getvalue() == 'B0321340000000N00000000EV0000000000\r\n'


def test_fix_with_extensions(writer):
    writer.write_fix_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])
    writer.write_fix(datetime.time(2, 3, 4), extensions=['023', 13, 2])

    assert writer.fp.getvalue() == '\r\n'.join([
        'I033638FXA3940SIU4143ENL',
        'B0203040000000N00000000EV000000000002313002',
    ]) + '\r\n'


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
    assert writer.fp.getvalue() == 'E123456PEV\r\n'


def test_event_with_text(writer):
    writer.write_event(datetime.time(1, 2, 3), 'PEV', 'This is a test')
    assert writer.fp.getvalue() == 'E010203PEVThis is a test\r\n'


def test_event_with_default_time(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_event('PEV')
    assert writer.fp.getvalue() == 'E032134PEV\r\n'


def test_event_with_default_time_and_text(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_event('PEV', 'Test')
    assert writer.fp.getvalue() == 'E032134PEVTest\r\n'


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
    assert writer.fp.getvalue() == 'F12345602523303\r\n'


def test_satellites_with_default_time(writer):
    with freeze_time("2012-01-14 03:21:34"):
        writer.write_satellites([2, 4, 99])
    assert writer.fp.getvalue() == 'F032134020499\r\n'


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

    assert writer.fp.getvalue() == '\r\n'.join([
        'J030810FXA1112SIU1315ENL',
        'K02030402313002',
    ]) + '\r\n'


def test_k_record_with_default_time(writer):
    writer.write_k_record_extensions([('FXA', 3), ('SIU', 2), ('ENL', 3)])

    with freeze_time("2012-01-14 03:21:34"):
        writer.write_k_record(['023', 13, 2])

    assert writer.fp.getvalue() == '\r\n'.join([
        'J030810FXA1112SIU1315ENL',
        'K03213402313002',
    ]) + '\r\n'


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
        'LPLTThis flight was my second 1000km attempt\r\n'


def test_comment_with_invalid_source(writer):
    with pytest.raises(ValueError) as ex:
        writer.write_comment('X', 'bla')

    assert 'Invalid source' in str(ex)
