import uuid
from dataclasses import dataclass, field
from datetime import time
from typing import List, Optional


from . import gml

# Airspace 1 ... n GeometryComponent
# GeometryComponent 1 ... 1 Volume
# Volume 1 ....  n Curves
#  -xor-
# Volume 1 ....  n Airspace (Dependency)


@dataclass
class ValDistanceVertical:
    """Vertical Distance Value"""
    value: float
    uom: str = "M"  # Unit of Measure (M=Meters, FT=Feet, FL=Flight Level)

    def __post_init__(self):
        if self.uom not in ["M", "FT", "FL"]:
            raise ValueError("UOM must be M, FT, or FL")


@dataclass
class AirspaceVolume:
    """AIXM AirspaceVolume Feature"""
    # Mandatory attributes
    gml_id: str = field(default_factory=lambda: f"asv_{uuid.uuid4().hex[:8]}")

    # Elements
    upper_limit: Optional[ValDistanceVertical] = None
    upper_limit_reference: Optional[str] = None           # AMSL, AGL, ...
    lower_limit: Optional[ValDistanceVertical] = None
    lower_limit_reference: Optional[str] = None           # AMSL, AGL, ...

    # Dependency relationships
    dependencies: List['AirspaceVolumeDependency'] = field(
        default_factory=list)
    curves: List['gml.Curve'] = field(default_factory=list)

    def add_curve(self, curve):
        self.curves.append(curve)

    def add_curves(self, curves):
        self.curves.extend(curves)

    def add_dependency(self, dependency):
        self.dependencies.append(dependency)


@dataclass
class AirspaceGeometryComponent:
    """AIXM AirspaceGeometryComponent - Association Class

    The role of the component in the airspace geometry. If the geometry of an
    airspace is composed of single volume, then the attributes of this
    association class may be left empty.
    """
    # Association attributes from AIXM spec
    operation: Optional[str] = None              # UNION, ADD, ...
    operation_sequence: Optional[int] = None

    # Reference to the actual geometry (Surface feature)
    volume: Optional['AirspaceVolume'] = None

    def set_operation(self, operation: str, sequence: int = 1):
        """Set the aggregation operation and sequence"""
        self.operation = operation
        self.operation_sequence = sequence

    def set_volume(self, volume: 'AirspaceVolume'):
        """Set the surface geometry for this component"""
        self.volume = volume


@dataclass
class AixmTimesheet:
    """
    AIXM Timesheet dataclass representing operational time periods.

    Attributes:
        time_reference: Time reference (UTC or LOCAL)
        start_date: Start date in MM-DD format
        end_date: End date in MM-DD format
        day: Day of the week
        day_til: End day of the week (optional)
        start_time: Start time in HH:MM format
        start_event: Start event (optional)
        start_time_relative_event: Start time relative to event (optional)
        start_event_interpretation: Start event interpretation (optional)
        end_time: End time in HH:MM format
        end_event: End event (optional)
        end_time_relative_event: End time relative to event (optional)
        end_event_interpretation: End event interpretation (optional)
        daylight_saving_adjust: Whether daylight saving time adjustments apply
        excluded: Whether this timesheet is excluded (optional)
    """
    time_reference: str  # "UTC" or "LOCAL"
    start_date: str      # Format: MM-DD
    end_date: str        # Format: MM-DD
    day: str             # "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"
    start_time: str      # Format: HH:MM
    end_time: str        # Format: HH:MM
    daylight_saving_adjust: bool  # True for "YES", False for "NO"

    # Optional fields
    # day_til: Optional[str] = None
    # start_event: Optional[str] = None
    # start_time_relative_event: Optional[str] = None
    # start_event_interpretation: Optional[str] = None
    # end_event: Optional[str] = None
    # end_time_relative_event: Optional[str] = None
    # end_event_interpretation: Optional[str] = None
    # excluded: Optional[bool] = None

    @property
    def start_time_obj(self) -> time:
        """Get start_time as time object."""
        return self.start_time if isinstance(self.start_time, time) else self._parse_time(self.start_time)

    @property
    def end_time_obj(self) -> time:
        """Get end_time as time object."""
        return self.end_time if isinstance(self.end_time, time) else self._parse_time(self.end_time)

    def _parse_time(self, time_str: str) -> time:
        """Parse time string to time object."""
        hours, minutes = map(int, time_str.split(':'))
        return time(hours, minutes)


@dataclass
class AirspaceActivation:
    """
    AIXM Airspace Activation
    """
    activity: Optional[str] = None           # UAV, ...
    status: Optional[str] = None           # ACTIVE

    timesheets: List[AixmTimesheet] = field(default_factory=list)

    def add_timesheet(self, timesheet: AixmTimesheet):
        self.timesheets.append(timesheet)


@dataclass
class Airspace:
    """AIXM Airspace Feature"""
    # Mandatory attributes
    gml_id: str = field(default_factory=lambda: f"as_{uuid.uuid4().hex[:8]}")

    # Is this Airspace referenced by another AirspaceVolume?
    is_referenced: Optional[bool] = False

    # Elements
    designator: Optional[str] = None
    name: Optional[str] = None
    type_airspace: Optional[str] = None       # CTR, FIR, ...
    localtype_airspace: Optional[str] = None  # CTR, FIR, ...
    # designator_type: Optional[CodeAirspaceDesignator] = None

    # Controlled airspace properties
    # controlling_unit: Optional[str] = None  # Reference to Unit
    class_airspace: Optional[str] = None  # A, B, C, D, E, F, G

    # Activation properties
    activation: Optional[AirspaceActivation] = None

    # Airspace volumes
    components: List[AirspaceGeometryComponent] = field(default_factory=list)

    def add_component(self, component: AirspaceGeometryComponent):
        """Add an AirspaceVolume to this Airspace"""
        self.components.append(component)


@dataclass
class AirspaceVolumeDependency:
    """AIXM AirspaceVolumeDependency Feature"""
    # Mandatory attributes
    gml_id: str = field(default_factory=lambda: f"avd_{uuid.uuid4().hex[:8]}")

    # Dependency elements
    # FULL_GEOMETRY, OVERLAPS, ...
    type_dependency: Optional[str] = None
    # Reference to dependent airspace
    dependency_airspace: Optional['Airspace'] = None
    # Reference to dependent volume
    dependency_volume: Optional['AirspaceVolume'] = None
    xlink: Optional['str'] = None


@dataclass
class GeoBorder:
    """AIXM GeoBorder Feature"""
    # Mandatory attributes
    gml_id: str = field(default_factory=lambda: f"avd_{uuid.uuid4().hex[:8]}")
    name: str = None
    curve: Optional[gml.Curve] = None
