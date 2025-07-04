import decimal
import urllib.request
import xml.etree.ElementTree as ET
from os import path

import aerofiles.aixm
import aerofiles.aixm.aixm

# import pytest


def download_aixm_example(data_dir: str):
    """Lädt die Beispiel-AIXM-Datei herunter und speichert sie im Unterverzeichnis DATA ."""
    url = "https://raw.githubusercontent.com/openAIP/openaip-aixm-to-geojson/723ec831789760254536657c5e76fec0a0b6b26d/tests/fixtures/aixm-airspace.xml"

    target_file = path.join(DATA, "aixm-airspace.xml")
    if not path.exists(target_file):
        urllib.request.urlretrieve(url, target_file)


DATA = path.join(path.dirname(path.realpath(__file__)), 'data')
ns = {
    'aixm': 'http://www.aixm.aero/schema/5.1.1',
    'gml': 'http://www.opengis.net/gml/3.2'
}

download_aixm_example(DATA)


# Fixtures ####################################################################

# Tests #######################################################################

def test_parser():
    parser = aerofiles.aixm.AixmAirspaceParser()
    airspaces, borders = parser.parse(path.join(DATA, "aixm-airspace.xml"))
    assert (len(airspaces) == 1583)
    assert (len(borders) == 11)


def test_parseTimesheet():

    tree = ET.parse(path.join(DATA, "aixm-airspace.xml"))
    root = tree.getroot()
    timesheet_element = root.find(
        './/aixm:Timesheet[@gml:id="id.ts.00bf0682-5479-40e5-8142-4437061fba18-ac-1-ac1-ts1"]', ns)

    parser = aerofiles.aixm.AixmAirspaceParser()
    timesheet = parser.parseTimesheet(timesheet_element)

    timesheet_expected = aerofiles.aixm.aixm.AixmTimesheet(
        time_reference='UTC', start_date=None, end_date=None, day='ANY', start_time='00:00', end_time='00:00', daylight_saving_adjust=False)

    assert (timesheet == timesheet_expected)


def test_parseAirspaceVolume():

    tree = ET.parse(path.join(DATA, "aixm-airspace.xml"))
    root = tree.getroot()
    volume_element = root.find(
        './/aixm:AirspaceVolume[@gml:id="id.asevol.48ceb197-a37a-46c6-941f-0733a1cf9141"]', ns)
    ET.dump(volume_element)

    parser = aerofiles.aixm.AixmAirspaceParser()
    volume = parser.parseAirspaceVolume(volume_element)

    volume_expected = aerofiles.aixm.aixm.AirspaceVolume(gml_id='id.asevol.48ceb197-a37a-46c6-941f-0733a1cf9141',
                                                         upper_limit=aerofiles.aixm.aixm.ValDistanceVertical(
                                                             value='1500', uom='FT'),
                                                         upper_limit_reference='SFC',
                                                         lower_limit=aerofiles.aixm.aixm.ValDistanceVertical(
                                                             value='0', uom='FT'),
                                                         lower_limit_reference='SFC',
                                                         dependencies=[],
                                                         curves=[aerofiles.aixm.gml.CurveImpl(segments=[aerofiles.aixm.gml.CircleSegment(center=aerofiles.aixm.gml.Position(latitude=53.915078111, longitude=10.040442194), radius=decimal.Decimal('2'))])])

    assert (volume == volume_expected)
