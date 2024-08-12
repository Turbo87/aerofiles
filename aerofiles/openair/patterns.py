import re

_INT = r'\d+'
_FLOAT = r'%s(?:\.%s)?' % (_INT, _INT)

_C1 = r'(%s):(%s):(%s)' % (_INT, _INT, _FLOAT)
_C2 = r'(%s):(%s)' % (_INT, _FLOAT)

_L = r'\s*%s\s*([NS])\s*%s\s*([EW])\s*'
_L1 = _L % (_C1, _C1)
_L2 = _L % (_C2, _C2)

LOCATION_FORMAT_1 = re.compile(_L1)
LOCATION_FORMAT_2 = re.compile(_L2)
