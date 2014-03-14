class TaskType:
    AAT = 'AAT'
    FAI_GENERAL = 'FAIGeneral'
    FAI_GOAL = 'FAIGoal'
    FAI_OUT_AND_RETURN = 'FAIOR'
    FAI_TRIANGLE = 'FAITriangle'
    MAT = 'MAT'
    MIXED = 'Mixed'
    RACING = 'RT'
    TOURING = 'Touring'


class PointType:
    START = 'Start'
    OPTIONAL_START = 'OptionalStart'
    AREA = 'Area'
    TURN = 'Turn'
    FINISH = 'Finish'


class ObservationZoneType:
    BGA_START = 'BGAStartSector'
    BGA_FIXED = 'BGAFixedCourse'
    BGA_ENHANCED = 'BGAEnhancedOption'
    CUSTOM_KEYHOLE = 'CustomKeyhole'
    CYLINDER = 'Cylinder'
    FAI_SECTOR = 'FAISector'
    KEYHOLE = 'Keyhole'
    LINE = 'Line'
    MAT_CYLINDER = 'MatCylinder'
    SECTOR = 'Sector'
    SYMMETRIC_QUADRANT = 'SymmetricQuadrant'


class AltitudeReference:
    AGL = 'AGL'
    MSL = 'MSL'
