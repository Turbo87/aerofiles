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


@pytest.fixture(params=[(1996, 12, 24), (2014, 1, 31), (2032, 8, 5)])
def date(request):
    return datetime.date(*request.param)


def test_date(writer, date):
    writer.write_date(date)
    assert writer.fp.getvalue() == date.strftime('HFDTE%d%m%y\r\n')


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
    with pytest.raises(ValueError):
        writer.write_fix_extensions([('42', 42)])


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


def test_task_metadata_without_turnpoints_fails(writer):
    with pytest.raises(ValueError):
        writer.write_task_metadata()


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


def test_default_task_point(writer):
    writer.write_task_point()
    assert writer.fp.getvalue() == 'C0000000N00000000E\r\n'
