from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Position:
    """Geographic position in decimal degrees"""
    latitude: float
    longitude: float

    def to_dms(self, coord_type: str) -> str:
        """Convert to degrees/minutes/seconds format for OpenAir"""
        value = self.latitude if coord_type == 'lat' else self.longitude
        abs_value = abs(value)
        degrees = int(abs_value)
        minutes = int((abs_value - degrees) * 60)
        seconds = ((abs_value - degrees) * 60 - minutes) * 60

        if coord_type == 'lat':
            direction = 'N' if value >= 0 else 'S'
        else:
            direction = 'E' if value >= 0 else 'W'

        return f"{degrees:02d}:{minutes:02d}:{seconds:05.2f} {direction}"


@dataclass
class GeometrySegment:
    """Base class for geometry segments"""
    pass


@dataclass
class PointSegment(GeometrySegment):
    """Circular airspace boundary"""
    point: Position


@dataclass
class CircleSegment(GeometrySegment):
    """Circular airspace boundary"""
    center: Position
    radius: float  # in nautical miles


@dataclass
class ArcSegment(GeometrySegment):
    """Arc segment of airspace boundary"""
    center: Position
    radius: float
    start_bearing: float
    end_bearing: float
    clockwise: bool = True


@dataclass
class LineSegment(GeometrySegment):
    """Line segment between two points"""
    start: Position
    end: Position


@dataclass
class ResolvedSegment(GeometrySegment):
    positions: List['Position'] = field(default_factory=list)
    parent: Optional[GeometrySegment] = None


@dataclass
class Curve:
    """Base class for geometry segments"""
    pass


@dataclass
class CurveRef(Curve):
    ref_id: str


@dataclass
class CurveImpl(Curve):
    segments: List[GeometrySegment] = field(default_factory=list)

    def add_segment(self, segment):
        self.segments.append(segment)

    def add_segments(self, segments):
        self.segments.extend(segments)


@dataclass
class Ring:
    curves: List[Curve] = field(default_factory=list)
