import decimal
import urllib.request
from json import load as load_json
from os import path

import aerofiles.aixm
import aerofiles.aixm.aixm

import pytest


# Fixtures ####################################################################

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
