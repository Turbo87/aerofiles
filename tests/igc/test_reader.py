# This Python file uses the following encoding: utf-8

import datetime
import os

from aerofiles.igc.reader import LowLevelReader
from aerofiles.igc.reader import Reader

import pytest


def test_decode_A_record():
    line = 'AXXXABC FLIGHT:1\r\n'
    expected_result = {
        'manufacturer': 'XXX',
        'id': 'ABC',
        'id_addition': 'FLIGHT:1'
    }

    assert LowLevelReader.decode_A_record(line) == expected_result


def test_decode_B_record():
    line = 'B1602455107126N00149300WA002880042919509020\r\n'
    expected_result = {
        'time': datetime.time(16, 2, 45),
        'lat': 51.118766666666666,
        'lon': -1.8216666666666668,
        'validity': 'A',
        'pressure_alt': 288,
        'gps_alt': 429,
        'start_index_extensions': 35,
        'extensions_string': '19509020'
    }

    assert LowLevelReader.decode_B_record(line) == expected_result


def test_process_B_record():

    """Check whether correct extension information is taken from B record"""

    # split up per extension for easy reading
    i_record = 'I08' + '3638FXA' + '3941ENL' + '4246TAS' + '4751GSP' + '5254TRT' + '5559VAT' + '6063OAT' + '6467ACZ'
    fix_record_extensions = LowLevelReader.decode_I_record(i_record)

    # split up per 10 to enable easy counting
    b_record = 'B093232520' + '2767N00554' + '786EA00128' '0019600600' '1145771529' + '3177005930' + '2770090'

    decoded_b_record = LowLevelReader.decode_B_record(b_record)
    processed_b_record = LowLevelReader.process_B_record(decoded_b_record, fix_record_extensions)

    # split per extension: 006 001 14577 15293 177 00593 0277 0090
    expected_values = [
        ('FXA', (36, 38), 6),
        ('ENL', (39, 41), 1),
        ('TAS', (42, 46), 14577),
        ('GSP', (47, 51), 15293),
        ('TRT', (52, 54), 177),
        ('VAT', (55, 59), 593),
        ('OAT', (60, 63), 277),
        ('ACZ', (64, 67), 90),
    ]

    for extension, bytes, expected_value in expected_values:
        assert {'bytes': bytes, 'extension_type': extension} in fix_record_extensions
        assert extension in processed_b_record
        assert expected_value == processed_b_record[extension]


def test_decode_invalid_B_record():
    """Test whether decoding invalid B record raise Error"""

    invalid_b_records = [
        'B1053175438931N0ÿÿÿøÈÐÀÀÜÐáÀÄÈàÔÀÄÈÌØÀÀÜÀÀ',
        'BÿÿÿøÄÀÈÌÄàÐäÐàààÁ8ÀÄÔÀäÈÌå��ÀÄàÔäÀ',
        'B1140ÿÿÿøÌÈÔÐÌÌààÑ8ÀÈÐÈÌàÌÕÀÀääÈÀÀäÔ',
        'B1309044931600N0153ÿÿÿøÐÀÄÍÀÄÔÌØÀÄÔÜØÀÀäÀ',
        'B10470349ÿÿÿøÌÔäØÕ8ÀÄÔÄÈàÜÙÀÄàÐÐÀÄäÀÜÀÀØÀ',
        'B11052249474ÿÿÿøÀÉ8ÀÄÔÀÜÜäÕÀÄÌÐÌÀÄÐÀÈÀÀÔÀ',
        'B12ÿÿÿøÐØÀÌÐäÐÈØäÝ8ÀÄÔÄÜÌÐÑÀÄØÐàÀÄÜÐÀÀÀÜÀÀÀ4)ÄÈ',
        'B1124185148269N9833N00553309EA0084800873000068000000',
        'B1245085122369N00614242EÿÿÿùÀÄÜØÄÀÄàÐäÀÀØÀ',
    ]

    for b_record in invalid_b_records:
        with pytest.raises(ValueError):
            LowLevelReader.decode_B_record(b_record)


def test_decode_C_record1():
    line = 'C150701213841160701000102 500K Tri\r\n'
    expected_result = {
        'subtype': 'task_info',
        'declaration_date': datetime.date(2001, 7, 15),
        'declaration_time': datetime.time(21, 38, 41),
        'flight_date': datetime.date(2001, 7, 16),
        'number': '0001',
        'num_turnpoints': 2,
        'description': '500K Tri'
    }

    assert LowLevelReader.decode_C_record(line) == expected_result


def test_decode_C_record2():
    line = 'C5111359N00101899W Lasham Clubhouse\r\n'
    expected_result = {
        'subtype': 'waypoint_info',
        'latitude': 51.18931666666667,
        'longitude': -1.03165,
        'description': 'Lasham Clubhouse'
    }

    assert LowLevelReader.decode_C_record(line) == expected_result


def test_decode_D_record():
    line = 'D20331\r\n'
    expected_result = {
        'qualifier': 'DGPS',
        'station_id': '0331'
    }

    assert LowLevelReader.decode_D_record(line) == expected_result


def test_decode_E_record():
    line = 'E160245PEV\r\n'
    expected_result = {
        'time': datetime.time(16, 2, 45),
        'tlc': 'PEV',
        'extension_string': ''
    }

    assert LowLevelReader.decode_E_record(line) == expected_result


def test_decode_F_record():
    line = 'F160240040609123624221821\r\n'
    expected_result = {
        'time': datetime.time(16, 2, 40),
        'satellites': ['04', '06', '09', '12', '36', '24', '22', '18', '21']
    }

    assert LowLevelReader.decode_F_record(line) == expected_result


def test_decode_G_record():
    line = 'GREJNGJERJKNJKRE31895478537H43982FJN9248F942389T433T\r\n'
    expected_result = 'REJNGJERJKNJKRE31895478537H43982FJN9248F942389T433T'

    assert LowLevelReader.decode_G_record(line) == expected_result


def test_decode_H_record():
    line = 'HFFXA035\r\n'
    expected_result = {
        'source': 'F',
        'fix_accuracy': 35
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_utc_date():
    line = 'HFDTE160701\r\n'
    expected_result = {
        'source': 'F',
        'utc_date': datetime.date(2001, 7, 16)
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_utc_date2():
    line = 'HFDTEDATE: 280709,01\r\n'
    expected_result = {
        'source': 'F',
        'utc_date': datetime.date(2009, 7, 28)
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_pilot():
    line = 'HFPLTPILOTINCHARGE: Bloggs Bill D\r\n'
    expected_result = {
        'source': 'F',
        'pilot': 'Bloggs Bill D'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_pilot_pwca_header():
    line = 'HFPLTPILOT: Bloggs Bill D\r\n'
    expected_result = {
        'source': 'F',
        'pilot': 'Bloggs Bill D'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_pilot_unkown_header():
    line = 'HFPLT XXX : Bloggs Bill D\r\n'
    expected_result = {
        'source': 'F',
        'pilot': 'Bloggs Bill D'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_copilot():
    line = 'HFCM2CREW2: Smith-Barry John A\r\n'
    expected_result = {
        'source': 'F',
        'copilot': 'Smith-Barry John A'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_glider_model():
    line = 'HFGTYGLIDERTYPE: Schleicher ASH-25\r\n'
    expected_result = {
        'source': 'F',
        'glider_model': 'Schleicher ASH-25'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_glider_registration():
    line = 'HFGIDGLIDERID: ABCD-1234\r\n'
    expected_result = {
        'source': 'F',
        'glider_registration': 'ABCD-1234'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_datum():
    line = 'HFDTM100GPSDATUM: WGS-1984\r\n'
    expected_result = {
        'source': 'F',
        'gps_datum': 'WGS-1984'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_firmware_revision():
    line = 'HFRFWFIRMWAREVERSION:6.4\r\n'
    expected_result = {
        'source': 'F',
        'firmware_revision': '6.4'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_hardware_revision():
    line = 'HFRHWHARDWAREVERSION:3.0\r\n'
    expected_result = {
        'source': 'F',
        'hardware_revision': '3.0'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_manufacturer_model():
    line = 'HFFTYFRTYPE: Manufacturer, Model\r\n'
    expected_result = {
        'source': 'F',
        'logger_manufacturer': 'Manufacturer',
        'logger_model': 'Model'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver():
    line = 'HFGPS:MarconiCanada, Superstar, 12ch, max10000m\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'MarconiCanada',
        'gps_model': 'Superstar',
        'gps_channels': 12,
        'gps_max_alt': {
            'value': 10000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver2():
    line = 'HFGPS:GLOBALTOP,FGPMMOPA6,66,max18000m\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'GLOBALTOP',
        'gps_model': 'FGPMMOPA6',
        'gps_channels': 66,
        'gps_max_alt': {
            'value': 18000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver3():
    line = 'HFGPS:GlobalTopPA6B,66ch,max18000m\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'GlobalTopPA6B',
        'gps_model': None,
        'gps_channels': 66,
        'gps_max_alt': {
            'value': 18000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver4():
    line = 'HFGPS:UBLOX,NEO-6G,16Ch,50000\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'UBLOX',
        'gps_model': 'NEO-6G',
        'gps_channels': 16,
        'gps_max_alt': {
            'value': 50000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver5():
    line = 'HFGPS:LX\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'LX',
        'gps_model': None,
        'gps_channels': None,
        'gps_max_alt': {
            'value': None,
            'unit': None
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver6():
    line = 'HFGPS:Cambridge 302,\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'Cambridge 302',
        'gps_model': None,
        'gps_channels': None,
        'gps_max_alt': {
            'value': None,
            'unit': None
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver7():
    line = 'HFGPSReceiver:Quectel,L80,22cm,18000m\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'Quectel',
        'gps_model': 'L80',
        'gps_channels': 22,
        'gps_max_alt': {
            'value': 18000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver8():
    line = 'HFGPSReceiver:Quectel,LSomething,32ch,50000\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'Quectel',
        'gps_model': 'LSomething',
        'gps_channels': 32,
        'gps_max_alt': {
            'value': 50000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gps_receiver9():
    line = 'HFGPSReceiver:u-blox,NEO-M8Q,22cm,70000\r\n'
    expected_result = {
        'source': 'F',
        'gps_manufacturer': 'u-blox',
        'gps_model': 'NEO-M8Q',
        'gps_channels': 72,
        'gps_max_alt': {
            'value': 70000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_gnss_alt():
    line = 'HFALG:GEO\r\n'
    expected_result = {
        'source': 'F',
        'gnss_altitude': 'GEO',
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_pressure_alt():
    line = 'HFALP:MSL\r\n'
    expected_result = {
        'source': 'F',
        'pressure_altitude': 'MSL',
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_pressure_sensor():
    line = 'HFPRSPRESSALTSENSOR: Sensyn, XYZ1111, max11000m\r\n'
    expected_result = {
        'source': 'F',
        'pressure_sensor_manufacturer': 'Sensyn',
        'pressure_sensor_model': 'XYZ1111',
        'pressure_sensor_max_alt': {
            'value': 11000,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_pressure_sensor2():
    line = 'HFPRSPressAltSensor:Intersema MS5534B,8191\r\n'
    expected_result = {
        'source': 'F',
        'pressure_sensor_manufacturer': 'Intersema',
        'pressure_sensor_model': 'MS5534B',
        'pressure_sensor_max_alt': {
            'value': 8191,
            'unit': 'm'
        }
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_competition_id():
    line = 'HFCIDCOMPETITIONID: XYZ-78910\r\n'
    expected_result = {
        'source': 'F',
        'competition_id': 'XYZ-78910'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_competition_class():
    line = 'HFCCLCOMPETITIONCLASS:15m Motor Glider\r\n'
    expected_result = {
        'source': 'F',
        'competition_class': '15m Motor Glider'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_time_zone_offset():
    line = 'HFTZNTIMEZONE:3\r\n'
    expected_result = {
        'source': 'F',
        'time_zone_offset': 3
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_time_zone_offset2():
    line = 'HFTZNTIMEZONE:11.00\r\n'
    expected_result = {
        'source': 'F',
        'time_zone_offset': 11
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_time_zone_offset3():
    line = 'HFTZNTIMEZONE:4.5\r\n'
    expected_result = {
        'source': 'F',
        'time_zone_offset': 4.5
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_time_zone_offset4():
    line = 'HFTZNTIMEZONE:-4.5\r\n'
    expected_result = {
        'source': 'F',
        'time_zone_offset': -4.5
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_mop_sensor():
    line = 'HFMOPSENSOR:MOP-(SN:1,ET=1375,0,1375,0,3.05V,p=0),Ver:0\r\n'
    expected_result = {
        'source': 'F',
        'mop_sensor': 'MOP-(SN:1,ET=1375,0,1375,0,3.05V,p=0),Ver:0'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_site():
    line = 'HFSITSite: lk15comp\r\n'
    expected_result = {
        'source': 'F',
        'site': 'lk15comp'
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_H_units_of_measure():
    line = 'HFUNTUnits: km,ft,kt'
    expected_result = {
        'source': 'F',
        'units_of_measure': ['km', 'ft', 'kt']
    }

    assert LowLevelReader.decode_H_record(line) == expected_result


def test_decode_I_record():
    line = 'I033638FXA3940SIU4143ENL\r\n'
    expected_result = [
        {'bytes': (36, 38), 'extension_type': 'FXA'},
        {'bytes': (39, 40), 'extension_type': 'SIU'},
        {'bytes': (41, 43), 'extension_type': 'ENL'}
    ]

    assert LowLevelReader.decode_I_record(line) == expected_result


def test_decode_J_record():
    line = 'J010812HDT\r\n'
    expected_result = [
        {'bytes': (8, 12), 'extension_type': 'HDT'}
    ]

    assert LowLevelReader.decode_J_record(line) == expected_result


def test_decode_K_record():
    line = 'K16024800090\r\n'
    expected_result = {
        'time': datetime.time(16, 2, 48),
        'value_string': '00090',
        'start_index': 7
    }

    assert LowLevelReader.decode_K_record(line) == expected_result


def test_decode_L_record():
    line = 'LXXXRURITANIAN STANDARD NATIONALS DAY 1\r\n'
    expected_result = {
        'source': 'XXX',
        'comment': 'RURITANIAN STANDARD NATIONALS DAY 1'
    }

    assert LowLevelReader.decode_L_record(line) == expected_result


def test_decode_latitude():
    assert LowLevelReader.decode_latitude('5117983N') == 51.29971666666667
    assert LowLevelReader.decode_latitude('3356767S') == -33.94611666666667


def test_decode_longitude():
    assert LowLevelReader.decode_longitude('00657383E') == 6.956383333333333
    assert LowLevelReader.decode_longitude('09942706W') == -99.71176666666666


def test_highlevel_reader():
    reader = Reader()

    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, 'data', 'example.igc'), 'r') as f:
        result = reader.read(f)

    assert result['logger_id'][1] == {
        'id': 'ABC',
        'id_addition': 'FLIGHT:1',
        'manufacturer': 'XXX'
    }

    fixes = result['fix_records'][1]
    assert len(fixes) == 9

    assert fixes[0]["datetime"] == datetime.datetime(2001, 7, 16, 16, 2, 40, tzinfo=datetime.UTC)
    # check that timezone is +3
    assert fixes[0]["datetime_local"].time() == datetime.time(19, 2, 40)

    # Check, that we have the next day, because the time is lower than the previous fix
    assert fixes[8]["datetime"].date() == datetime.date(2001, 7, 17)

    assert result['task'][1]['declaration_date'] == datetime.date(2001, 7, 15)
    assert result['task'][1]['declaration_time'] == datetime.time(21, 38, 41)
    assert result['task'][1]['flight_date'] == datetime.date(2001, 7, 16)
    assert result['task'][1]['num_turnpoints'] == 2
    assert result['task'][1]['description'] == '500K Tri'
    assert result['task'][1]['number'] == '0001'
    assert len(result['task'][1]['waypoints']) == 6

    assert len(result['dgps_records'][1]) == 1

    assert len(result['event_records'][1]) == 2

    assert len(result['satellite_records'][1]) == 2

    assert len(result['security_records'][1]) == 5

    assert result['header'][1] == {
        'competition_class': '15m Motor Glider',
        'competition_id': 'XYZ-78910',
        'copilot': 'Smith-Barry John A',
        'firmware_revision': '6.4',
        'fix_accuracy': 35,
        'glider_model': 'Schleicher ASH-25',
        'glider_registration': 'ABCD-1234',
        'gps_channels': 12,
        'gps_datum': 'WGS-1984',
        'gps_manufacturer': 'MarconiCanada',
        'gps_max_alt': {
            'unit': 'm',
            'value': 10000},
        'gps_model': 'Superstar',
        'hardware_revision': '3.0',
        'logger_manufacturer': 'Manufacturer',
        'logger_model': 'Model',
        'pilot': 'Bloggs Bill D',
        'pressure_sensor_model': 'XYZ1111',
        'pressure_sensor_manufacturer': 'Sensyn',
        'pressure_sensor_max_alt': {
            'unit': 'm',
            'value': 11000},
        'time_zone_offset': 3,
        'utc_date': datetime.date(2001, 7, 16)
    }

    assert len(result['fix_record_extensions'][1]) == 3
    assert result['fix_record_extensions'][1] == [
        {'bytes': (36, 38), 'extension_type': 'FXA'},
        {'bytes': (39, 40), 'extension_type': 'SIU'},
        {'bytes': (41, 43), 'extension_type': 'ENL'}
    ]

    assert len(result['k_record_extensions'][1]) == 1
    assert result['k_record_extensions'][1] == [
        {'bytes': (8, 12), 'extension_type': 'HDT'}
    ]

    assert len(result['k_records'][1]) == 1

    assert len(result['comment_records'][1]) == 2


def test_highlevel_reader_examples():
    reader = Reader()

    # We try to read in a number of example IGC files and make
    # sure, that there is not parsing error
    cur_dir = os.path.dirname(__file__)
    directory = os.path.join(cur_dir, 'data')
    for entry in os.listdir(directory):
        filename = os.path.join(directory, entry)
        with open(os.path.join(filename), 'r') as f:
            result = reader.read(f)
            for key in result:
                # Assert, that there are no parse errors
                if len(result[key][0]) != 0:
                    assert len(result[key][0]) == 0, "%s %s" % (filename, key)
