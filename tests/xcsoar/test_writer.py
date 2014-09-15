# -*- coding: utf-8 -*-

import pytest

import os.path
import datetime

from io import BytesIO

from aerofiles.xcsoar import (
    Writer, TaskType, PointType, ObservationZoneType, AltitudeReference
)

FOLDER = os.path.dirname(os.path.realpath(__file__))


@pytest.fixture()
def output():
    return BytesIO()


@pytest.fixture()
def writer(output):
    return Writer(output)


def read_file(filename):
    path = os.path.join(FOLDER, 'data', filename)
    return open(path, 'rb').read()


def test_write_line(writer):
    writer.write_line('line')
    assert writer.fp.getvalue() == b'line\n'


def test_write_line_with_utf8(writer):
    writer.write_line(u'Köln')
    assert writer.fp.getvalue() == b'K\xc3\xb6ln\n'


def test_write_line_with_latin1(output):
    writer = Writer(output, 'latin1')
    writer.write_line(u'Köln')
    assert writer.fp.getvalue() == b'K\xf6ln\n'


def test_write_sample_task(writer):
    with writer.write_task(
        start_max_height_ref=AltitudeReference.AGL,
        start_max_height=0,
        start_max_speed=0,
        start_requires_arm=False,
        finish_min_height_ref=AltitudeReference.AGL,
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


def test_write_sample_task_2(writer):
    with writer.write_task(
        aat_min_time=datetime.timedelta(hours=2.5),
        fai_finish=False,
        finish_min_height=200,
        finish_min_height_ref=AltitudeReference.AGL,
        start_close_time=datetime.time(14, 30),
        start_max_height=1600,
        start_max_height_ref=AltitudeReference.MSL,
        start_max_speed=47.2222,
        start_open_time=datetime.time(13, 30),
        start_requires_arm=True,
        type=TaskType.AAT,
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
                type=ObservationZoneType.LINE,
                length=20000,
            )

        with writer.write_point(type=PointType.AREA):
            writer.write_waypoint(
                name='Dahlemer Binz',
                comment='Flugplatz',
                id=1064,
                altitude=579,
                latitude=50.4056,
                longitude=6.52888,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.CYLINDER,
                radius=20000,
            )

        with writer.write_point(type=PointType.AREA):
            writer.write_waypoint(
                name='Ailertchen',
                comment='Flugplatz',
                id=67,
                altitude=469,
                latitude=50.5925,
                longitude=7.94445,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.CYLINDER,
                radius=30000,
            )

        with writer.write_point(type=PointType.AREA):
            writer.write_waypoint(
                name='Meschede Schuer',
                comment='Flugplatz',
                id=3737,
                altitude=439,
                latitude=51.3028,
                longitude=8.23945,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.CYLINDER,
                radius=30000,
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
                type=ObservationZoneType.LINE,
                length=1000,
            )

    assert writer.fp.getvalue() == read_file('AAT.tsk')


def test_write_sample_task_3(writer):
    with writer.write_task(
        finish_min_height=200,
        finish_min_height_ref=AltitudeReference.AGL,
        start_max_speed=55.5556,
        start_open_time=datetime.time(12, 13),
        type=TaskType.RACING,
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
                type=ObservationZoneType.LINE,
                length=20000,
            )

        with writer.write_point(type=PointType.TURN):
            writer.write_waypoint(
                name='Ailertchen',
                comment='Flugplatz',
                id=67,
                altitude=469,
                latitude=50.5925,
                longitude=7.94445,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.KEYHOLE,
            )

        with writer.write_point(type=PointType.TURN):
            writer.write_waypoint(
                name='Meschede Schuer',
                comment='Flugplatz',
                id=3737,
                altitude=439,
                latitude=51.3028,
                longitude=8.23945,
            )

            writer.write_observation_zone(
                type=ObservationZoneType.KEYHOLE,
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
                type=ObservationZoneType.CYLINDER,
                radius=1000,
            )

    assert writer.fp.getvalue() == read_file('Racing.tsk')
