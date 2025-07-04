import urllib.request
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

def test_converter():
    parser = aerofiles.aixm.AixmAirspaceParser()
    airspaces, borders = parser.parse(path.join(DATA, "aixm-airspace.xml"))
    converter = aerofiles.aixm.AixmOpenairConverter(airspaces, borders)
    openairs = converter.convert_airspaces()
    assert (len(openairs) == 1527)
    openairs = converter.convert_airspaces(only_referenced_airspaces=False)
    assert (len(openairs) == 2470)


def test_converter_resolved():
    parser = aerofiles.aixm.AixmAirspaceParser()
    airspaces, borders = parser.parse(path.join(DATA, "aixm-airspace.xml"))
    parser.resolve()
    converter = aerofiles.aixm.AixmOpenairConverter(airspaces, borders)
    openairs = converter.convert_airspaces()
    assert (len(openairs) == 1527)
    openairs = converter.convert_airspaces(only_referenced_airspaces=False)
    assert (len(openairs) == 2470)
