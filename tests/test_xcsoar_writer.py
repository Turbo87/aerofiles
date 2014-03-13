import pytest

import os.path
import datetime

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from aerofiles.xcsoar import Writer, TaskType, PointType, ObservationZoneType

FOLDER = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def output():
    return StringIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def read_file(filename):
    path = os.path.join(FOLDER, 'data', filename)
    return open(path).read()


def test_write_sample_task(writer):
    with writer.write_task(
        start_max_height_ref='AGL',
        start_max_height=0,
        start_max_speed=0,
        start_requires_arm=0,
        finish_min_height_ref='AGL',
        finish_min_height=0,
        fai_finish=True,
        aat_min_time=datetime.timedelta(hours=3),
        type=TaskType.FAI_GENERAL,
    ):
        with writer.write_point(type=PointType.START):
            writer.write_waypoint(
                name='Aachen Merzbruc',
                comment='Flugplatz',
                id=3,
                altitude=189,
                latitude=50.8231,
                longitude=6.18638,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.FAI_SECTOR,
            )

        with writer.write_point(type=PointType.TURN):
            writer.write_waypoint(
                name='Dillingen',
                comment='Flugplatz',
                id=1630,
                altitude=239,
                latitude=49.3861,
                longitude=6.74862,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.FAI_SECTOR,
            )

        with writer.write_point(type=PointType.TURN):
            writer.write_waypoint(
                name='Fredeburg Hunau',
                comment='SENDER',
                id=2453,
                altitude=779,
                latitude=51.2061,
                longitude=8.37722,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.FAI_SECTOR,
            )

        with writer.write_point(type=PointType.FINISH):
            writer.write_waypoint(
                name='Aachen Merzbruc',
                comment='Flugplatz',
                id=3,
                altitude=189,
                latitude=50.8231,
                longitude=6.18638,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.FAI_SECTOR,
            )

    assert writer.fp.getvalue() == read_file('FAI.tsk')
