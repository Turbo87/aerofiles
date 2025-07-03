import decimal
import urllib.request
from json import load as load_json
from os import path

import aerofiles.aixm
import aerofiles.aixm.aixm

import pytest


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

@pytest.fixture
def json():
    with open(path.join(DATA, 'sample.json')) as fp:
        return load_json(fp)


@pytest.fixture
def low_level_json():
    with open(path.join(DATA, 'sample-low-level.json')) as fp:
        return load_json(fp)


# Tests #######################################################################

def test_resolve_curve():

    segment = aerofiles.aixm.gml.CircleSegment(center=aerofiles.aixm.gml.Position(
        latitude=53.915078111, longitude=10.040442194), radius=decimal.Decimal('2'))
    expected_segment = aerofiles.aixm.gml.ResolvedSegment(positions=[
        aerofiles.aixm.gml.Position(
            latitude=53.948356209194145, longitude=10.040442194),
        aerofiles.aixm.gml.Position(
            latitude=53.89843906190293, longitude=10.089257983419508),
        aerofiles.aixm.gml.Position(
            latitude=53.881800012805854, longitude=10.040442194),
        aerofiles.aixm.gml.Position(latitude=53.93171716009707, longitude=9.991626404580494)],
        parent=aerofiles.aixm.gml.CircleSegment(center=aerofiles.aixm.gml.Position(latitude=53.915078111, longitude=10.040442194),
                                                radius=decimal.Decimal('2')))

    resolver = aerofiles.aixm.AixmGeometryResolver(120)
    resolved_segment = resolver.resolve_segment(segment)
    assert (resolved_segment == expected_segment)
